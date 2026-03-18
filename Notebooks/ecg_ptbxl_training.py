#!/usr/bin/env python3
"""
================================================================================
 ZRay ECG — PTB-XL 12-Lead ECG Classification (1D-ResNet)
 -------------------------------------------------------------------------
 Production-ready training script for Google Colab.
 Downloads the PTB-XL v1.0.3 dataset from PhysioNet via wget, trains a
 1D Residual Network, generates presentation-quality visualizations, and
 exports the model to an edge-optimized ONNX format with INT8 dynamic
 quantization.

 Superclasses: NORM . MI . STTC . CD . HYP
 Target accuracy: >90%  |  Export: ONNX opset-14 (FP32 + INT8)
================================================================================
"""

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §1  ENVIRONMENT SETUP & IMPORTS                                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import subprocess
import sys

def _pip_install(*packages):
    """Silently install packages that aren't already available."""
    for pkg in packages:
        try:
            __import__(pkg.split("==")[0].split("[")[0])
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

_pip_install("wfdb", "onnx", "onnxruntime", "onnxscript")

import os
import ast
import time
import copy
import warnings

import numpy as np
import pandas as pd
import wfdb
import matplotlib
# In Colab, matplotlib renders inline by default -- no backend override needed.
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    accuracy_score,
)
from sklearn.preprocessing import MultiLabelBinarizer

warnings.filterwarnings("ignore")

# ── Dataset download via wget ─────────────────────────────────────────────────
# Downloads PTB-XL v1.0.3 from PhysioNet.  wget flags:
#   -r   recursive      -N   timestamping (skip if up-to-date)
#   -c   continue       -np  no parent directory traversal
DOWNLOAD_DIR = "/content/ptb-xl-data"
PHYSIONET_URL = "https://physionet.org/files/ptb-xl/1.0.3/"

if not os.path.isfile(os.path.join(DOWNLOAD_DIR, "physionet.org/files/ptb-xl/1.0.3/ptbxl_database.csv")):
    print("[INFO] Downloading PTB-XL v1.0.3 from PhysioNet (~2 GB) ...")
    subprocess.run(
        [
            "wget", "-r", "-N", "-c", "-np",
            "--directory-prefix", DOWNLOAD_DIR,
            "--no-verbose",
            PHYSIONET_URL,
        ],
        check=True,
    )
    print("[INFO] Download complete.")
else:
    print("[INFO] PTB-XL dataset already present -- skipping download.")

# ── Global paths ──────────────────────────────────────────────────────────────
# After wget -r, files land under <DOWNLOAD_DIR>/physionet.org/files/ptb-xl/1.0.3/
DATA_DIR   = os.path.join(DOWNLOAD_DIR, "physionet.org", "files", "ptb-xl", "1.0.3")
OUTPUT_DIR = "/content/working"
PLOT_DIR   = os.path.join(OUTPUT_DIR, "training_plots")
ONNX_DIR   = os.path.join(OUTPUT_DIR, "deployment", "onnx_assets")
MODEL_PATH = os.path.join(OUTPUT_DIR, "best_ecg_model.pth")

os.makedirs(PLOT_DIR, exist_ok=True)
os.makedirs(ONNX_DIR, exist_ok=True)

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark     = False

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Device: {DEVICE}")

# ── Hyperparameters ───────────────────────────────────────────────────────────
BATCH_SIZE    = 64
NUM_EPOCHS    = 50
LEARNING_RATE = 1e-3
WEIGHT_DECAY  = 1e-4
PATIENCE      = 7         # early-stopping patience
NUM_CLASSES   = 5
SUPERCLASSES  = ["NORM", "MI", "STTC", "CD", "HYP"]

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §2  DATASET LOADING & PREPROCESSING                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§2  Loading PTB-XL dataset …")
print("=" * 72)

# ── 2.1  Load metadata ───────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, "ptbxl_database.csv"), index_col="ecg_id")
df.scp_codes = df.scp_codes.apply(ast.literal_eval)       # str → dict

# ── 2.2  Build superclass mapping from scp_statements.csv ────────────────────
scp_df = pd.read_csv(os.path.join(DATA_DIR, "scp_statements.csv"), index_col=0)
# Keep only entries that belong to one of the 5 superclasses
scp_to_super = {}
for idx, row in scp_df.iterrows():
    if isinstance(row.get("diagnostic_class"), str) and row["diagnostic_class"] in SUPERCLASSES:
        scp_to_super[idx] = row["diagnostic_class"]

def _aggregate_superclasses(scp_dict):
    """Return a set of superclass labels for a given scp_codes dict."""
    labels = set()
    for code in scp_dict:
        if code in scp_to_super:
            labels.add(scp_to_super[code])
    return labels

df["superclass_set"] = df.scp_codes.apply(_aggregate_superclasses)

# Drop rows with no superclass labels (non-diagnostic records)
df = df[df.superclass_set.apply(len) > 0].copy()
print(f"[INFO] Records after filtering: {len(df)}")

# ── 2.3  Multi-label binarization ────────────────────────────────────────────
mlb = MultiLabelBinarizer(classes=SUPERCLASSES)
labels_np = mlb.fit_transform(df.superclass_set)            # shape (N, 5)
print(f"[INFO] Label matrix shape: {labels_np.shape}")

# ── 2.4  Load 100 Hz signals via WFDB ────────────────────────────────────────
print("[INFO] Reading 100 Hz waveform files (this may take a few minutes) …")

def _load_signal(row):
    """Load a single 100 Hz ECG record, returning (1000, 12) array."""
    # filename_lr contains the *relative* path to the 100 Hz signal
    rec_path = os.path.join(DATA_DIR, row.filename_lr)
    record = wfdb.rdrecord(rec_path)
    return record.p_signal                                  # (1000, 12)

signals = np.array([_load_signal(row) for _, row in df.iterrows()], dtype=np.float32)
# signals shape: (N, 1000, 12)

# Transpose to PyTorch Conv1d layout: (N, Channels=12, Length=1000)
signals = signals.transpose(0, 2, 1)                        # (N, 12, 1000)
print(f"[INFO] Signal tensor shape: {signals.shape}")

# ── 2.5  Train / Test split by strat_fold ────────────────────────────────────
folds = df.strat_fold.values
train_mask = folds != 10
test_mask  = folds == 10

X_train_np, X_test_np = signals[train_mask], signals[test_mask]
y_train_np, y_test_np = labels_np[train_mask], labels_np[test_mask]

print(f"[INFO] Train: {X_train_np.shape[0]}  |  Test: {X_test_np.shape[0]}")

# ── 2.6  Per-lead standard scaling (fit on train only) ───────────────────────
# Compute mean & std per channel across the training set
# Shape of mean/std: (12, 1) for broadcasting over the time axis
train_mean = X_train_np.mean(axis=(0, 2), keepdims=True)     # (1, 12, 1)
train_std  = X_train_np.std(axis=(0, 2), keepdims=True) + 1e-8

X_train_np = (X_train_np - train_mean) / train_std
X_test_np  = (X_test_np  - train_mean) / train_std

# Save scaling stats for the inference class later
SCALING_MEAN = train_mean.squeeze()                          # (12,)
SCALING_STD  = train_std.squeeze()                           # (12,)

# ── 2.7  Create DataLoaders ──────────────────────────────────────────────────
train_ds = TensorDataset(
    torch.tensor(X_train_np, dtype=torch.float32),
    torch.tensor(y_train_np, dtype=torch.float32),
)
test_ds = TensorDataset(
    torch.tensor(X_test_np, dtype=torch.float32),
    torch.tensor(y_test_np, dtype=torch.float32),
)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          num_workers=2, pin_memory=True, drop_last=False)
test_loader  = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=2, pin_memory=True)

print("[INFO] DataLoaders ready.\n")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §3  1D-RESNET MODEL ARCHITECTURE                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class ResidualBlock1D(nn.Module):
    """
    Pre-activation residual block for 1-D time-series:
        Conv1d → BN → ReLU → Conv1d → BN → (+skip) → ReLU → Dropout
    Includes an optional down-sampling skip connection when stride > 1
    or when the channel dimension changes.
    """

    def __init__(self, in_channels, out_channels, kernel_size=7, stride=1,
                 dropout=0.2):
        super().__init__()
        padding = kernel_size // 2

        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size,
                               stride=stride, padding=padding, bias=False)
        self.bn1   = nn.BatchNorm1d(out_channels)
        self.relu  = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size,
                               stride=1, padding=padding, bias=False)
        self.bn2   = nn.BatchNorm1d(out_channels)

        self.dropout = nn.Dropout(p=dropout)

        # Skip / shortcut connection
        self.skip = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.skip = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1,
                          stride=stride, bias=False),
                nn.BatchNorm1d(out_channels),
            )

    def forward(self, x):
        identity = self.skip(x)

        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += identity
        out = self.relu(out)
        out = self.dropout(out)
        return out


class ECGResNet1D(nn.Module):
    """
    1D Residual Network for 12-lead ECG classification.

    Architecture:
        InputConv (12 → 64) → 4 ResidualStages → AdaptiveAvgPool → FC → 5 logits

    Stages progressively double the channel width while halving the temporal
    resolution (stride-2 in the first block of each stage).
    """

    def __init__(self, in_channels=12, num_classes=5, dropout=0.3):
        super().__init__()

        # ── Initial convolution ───────────────────────────────────────────
        self.input_block = nn.Sequential(
            nn.Conv1d(in_channels, 64, kernel_size=15, stride=2,
                      padding=7, bias=False),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=3, stride=2, padding=1),
        )

        # ── Residual stages ───────────────────────────────────────────────
        self.stage1 = self._make_stage(64,  64,  num_blocks=2, stride=1, dropout=dropout)
        self.stage2 = self._make_stage(64,  128, num_blocks=2, stride=2, dropout=dropout)
        self.stage3 = self._make_stage(128, 256, num_blocks=2, stride=2, dropout=dropout)
        self.stage4 = self._make_stage(256, 512, num_blocks=2, stride=2, dropout=dropout)

        # ── Classifier head ───────────────────────────────────────────────
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.classifier  = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(512, num_classes),
        )

    @staticmethod
    def _make_stage(in_ch, out_ch, num_blocks, stride, dropout):
        layers = [ResidualBlock1D(in_ch, out_ch, stride=stride, dropout=dropout)]
        for _ in range(1, num_blocks):
            layers.append(ResidualBlock1D(out_ch, out_ch, stride=1, dropout=dropout))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.input_block(x)
        x = self.stage1(x)
        x = self.stage2(x)
        x = self.stage3(x)
        x = self.stage4(x)
        x = self.global_pool(x)
        # ONNX-safe flatten (no .view())
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x


# ── Instantiate & print summary ──────────────────────────────────────────────
model = ECGResNet1D(in_channels=12, num_classes=NUM_CLASSES, dropout=0.3).to(DEVICE)
total_params = sum(p.numel() for p in model.parameters())
print(f"[MODEL] ECGResNet1D — {total_params:,} parameters")
print(model)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §4  TRAINING LOOP & OPTIMIZATION                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§4  Training …")
print("=" * 72)

criterion = nn.BCEWithLogitsLoss()
optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE,
                        weight_decay=WEIGHT_DECAY)

steps_per_epoch = len(train_loader)
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer,
    max_lr=LEARNING_RATE,
    steps_per_epoch=steps_per_epoch,
    epochs=NUM_EPOCHS,
    pct_start=0.3,
    anneal_strategy="cos",
)

# ── Metric history ────────────────────────────────────────────────────────────
history = {
    "train_loss": [], "val_loss": [],
    "train_acc":  [], "val_acc":  [],
    "val_auc":    [],
}

best_val_loss  = float("inf")
best_model_wts = copy.deepcopy(model.state_dict())
epochs_no_improve = 0


def _threshold_accuracy(logits, targets, threshold=0.5):
    """Compute sample-averaged accuracy from raw logits and binary targets."""
    preds = (torch.sigmoid(logits) >= threshold).float()
    correct = (preds == targets).float().mean()
    return correct.item()


for epoch in range(1, NUM_EPOCHS + 1):
    t0 = time.time()

    # ── Training phase ────────────────────────────────────────────────────
    model.train()
    running_loss, running_acc, n_batches = 0.0, 0.0, 0

    for xb, yb in train_loader:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)

        optimizer.zero_grad()
        logits = model(xb)
        loss   = criterion(logits, yb)
        loss.backward()
        optimizer.step()
        scheduler.step()

        running_loss += loss.item()
        running_acc  += _threshold_accuracy(logits, yb)
        n_batches    += 1

    train_loss = running_loss / n_batches
    train_acc  = running_acc  / n_batches

    # ── Validation phase ──────────────────────────────────────────────────
    model.eval()
    val_loss, val_acc, val_n = 0.0, 0.0, 0
    all_val_logits, all_val_labels = [], []

    with torch.no_grad():
        for xb, yb in test_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            logits = model(xb)

            val_loss += criterion(logits, yb).item()
            val_acc  += _threshold_accuracy(logits, yb)
            val_n    += 1

            all_val_logits.append(logits.cpu())
            all_val_labels.append(yb.cpu())

    val_loss /= val_n
    val_acc  /= val_n

    # Macro AUC
    all_val_logits = torch.cat(all_val_logits).numpy()
    all_val_labels = torch.cat(all_val_labels).numpy()
    all_val_probs  = 1.0 / (1.0 + np.exp(-all_val_logits))  # sigmoid

    try:
        val_auc = roc_auc_score(all_val_labels, all_val_probs, average="macro")
    except ValueError:
        val_auc = 0.0

    elapsed = time.time() - t0

    # ── Logging ───────────────────────────────────────────────────────────
    history["train_loss"].append(train_loss)
    history["val_loss"].append(val_loss)
    history["train_acc"].append(train_acc)
    history["val_acc"].append(val_acc)
    history["val_auc"].append(val_auc)

    print(
        f"Epoch {epoch:02d}/{NUM_EPOCHS} │ "
        f"loss {train_loss:.4f}/{val_loss:.4f} │ "
        f"acc {train_acc:.4f}/{val_acc:.4f} │ "
        f"AUC {val_auc:.4f} │ "
        f"lr {scheduler.get_last_lr()[0]:.2e} │ "
        f"{elapsed:.1f}s"
    )

    # ── Early stopping ────────────────────────────────────────────────────
    if val_loss < best_val_loss:
        best_val_loss  = val_loss
        best_model_wts = copy.deepcopy(model.state_dict())
        epochs_no_improve = 0
        torch.save(best_model_wts, MODEL_PATH)
        print(f"  ↳ Best model saved ({val_loss:.4f})")
    else:
        epochs_no_improve += 1
        if epochs_no_improve >= PATIENCE:
            print(f"\n[EARLY STOP] No improvement for {PATIENCE} epochs.")
            break

    # ── Memory cleanup ────────────────────────────────────────────────────
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# Restore best weights
model.load_state_dict(best_model_wts)
print(f"\n[INFO] Training complete. Best val loss: {best_val_loss:.4f}")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §5  PRESENTATION VISUALIZATIONS                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§5  Generating presentation visualizations …")
print("=" * 72)

sns.set_theme(style="whitegrid", font_scale=1.2)
epochs_range = range(1, len(history["train_loss"]) + 1)

# ── 5.1  Loss curves ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(epochs_range, history["train_loss"], "o-", label="Train Loss", linewidth=2)
ax.plot(epochs_range, history["val_loss"],   "s-", label="Val Loss",   linewidth=2)
ax.set_xlabel("Epoch")
ax.set_ylabel("BCEWithLogitsLoss")
ax.set_title("Training vs Validation Loss")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "loss_curves.png"), dpi=200)
plt.close(fig)
print(f"  ✓ Saved loss_curves.png")

# ── 5.2  Accuracy curves ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(epochs_range, history["train_acc"], "o-", label="Train Accuracy", linewidth=2)
ax.plot(epochs_range, history["val_acc"],   "s-", label="Val Accuracy",   linewidth=2)
ax.set_xlabel("Epoch")
ax.set_ylabel("Accuracy")
ax.set_title("Training vs Validation Accuracy")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "accuracy_curves.png"), dpi=200)
plt.close(fig)
print(f"  ✓ Saved accuracy_curves.png")

# ── 5.3  Confusion matrix heatmap (test set) ─────────────────────────────────
# Re-run inference on test set with best model
model.eval()
all_logits, all_labels = [], []
with torch.no_grad():
    for xb, yb in test_loader:
        xb = xb.to(DEVICE)
        logits = model(xb)
        all_logits.append(logits.cpu())
        all_labels.append(yb)

all_logits = torch.cat(all_logits).numpy()
all_labels = torch.cat(all_labels).numpy()
all_probs  = 1.0 / (1.0 + np.exp(-all_logits))
all_preds  = (all_probs >= 0.5).astype(int)

# Per-class confusion matrix (one per superclass, arranged in a single heatmap)
# We create a combined (5×2×2) view: for each class, compute TP/FP/FN/TN
fig, axes = plt.subplots(1, 5, figsize=(22, 4))
for i, cls_name in enumerate(SUPERCLASSES):
    cm = confusion_matrix(all_labels[:, i], all_preds[:, i])
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[i],
                xticklabels=["Neg", "Pos"], yticklabels=["Neg", "Pos"])
    axes[i].set_title(cls_name)
    axes[i].set_xlabel("Predicted")
    axes[i].set_ylabel("Actual")
fig.suptitle("Per-Class Confusion Matrices (Test Set)", fontsize=14, y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "confusion_matrix.png"), dpi=200,
            bbox_inches="tight")
plt.close(fig)
print(f"  ✓ Saved confusion_matrix.png")

# ── 5.4  ROC-AUC curves ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
colors = sns.color_palette("husl", NUM_CLASSES)
for i, cls_name in enumerate(SUPERCLASSES):
    fpr, tpr, _ = roc_curve(all_labels[:, i], all_probs[:, i])
    auc_val = roc_auc_score(all_labels[:, i], all_probs[:, i])
    ax.plot(fpr, tpr, color=colors[i], linewidth=2,
            label=f"{cls_name} (AUC = {auc_val:.3f})")
ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC-AUC Curves — 5 Superclasses")
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "roc_auc_curves.png"), dpi=200)
plt.close(fig)
print(f"  ✓ Saved roc_auc_curves.png")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §6  PRODUCTION INFERENCE INTERFACE                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class ZRayECGInference:
    """
    Clean inference class for 12-lead ECG classification.

    Usage:
        engine = ZRayECGInference("best_ecg_model.pth", device="cpu")
        label, confidence, probs = engine.predict(ecg_array)

    Parameters
    ----------
    model_path : str
        Path to the saved `best_ecg_model.pth` state dict.
    device : str
        PyTorch device string ("cpu" or "cuda").
    scaling_mean : np.ndarray
        Per-lead mean (shape (12,)) from training set.
    scaling_std : np.ndarray
        Per-lead std (shape (12,)) from training set.
    """

    CLASS_NAMES = ["NORM", "MI", "STTC", "CD", "HYP"]

    def __init__(self, model_path, device="cpu",
                 scaling_mean=None, scaling_std=None):
        self.device = torch.device(device)

        # Load model architecture + weights
        self.model = ECGResNet1D(in_channels=12, num_classes=5, dropout=0.0)
        state = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()

        # Scaling statistics
        self.mean = scaling_mean if scaling_mean is not None else np.zeros(12)
        self.std  = scaling_std  if scaling_std  is not None else np.ones(12)

    def predict(self, ecg_signal: np.ndarray):
        """
        Run inference on a single 12-lead ECG.

        Parameters
        ----------
        ecg_signal : np.ndarray, shape (1, 12, 1000)
            Raw 100 Hz ECG signal (12 leads × 1000 time-steps).

        Returns
        -------
        top_label   : str     — Predicted superclass name.
        confidence  : float   — Confidence percentage (0–100).
        all_probs   : dict    — {class_name: probability} for all 5 classes.
        """
        assert ecg_signal.shape == (1, 12, 1000), \
            f"Expected shape (1, 12, 1000), got {ecg_signal.shape}"

        # Apply training-set scaling
        scaled = ecg_signal.copy().astype(np.float32)
        for ch in range(12):
            scaled[0, ch, :] = (scaled[0, ch, :] - self.mean[ch]) / (self.std[ch] + 1e-8)

        # Inference
        tensor = torch.tensor(scaled, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            logits = self.model(tensor)
        probs = torch.sigmoid(logits).cpu().numpy().squeeze()

        # Outputs
        top_idx    = int(np.argmax(probs))
        top_label  = self.CLASS_NAMES[top_idx]
        confidence = float(probs[top_idx]) * 100.0
        all_probs  = {name: float(p) for name, p in zip(self.CLASS_NAMES, probs)}

        return top_label, confidence, all_probs


# ── Quick demo ────────────────────────────────────────────────────────────────
print("\n" + "=" * 72)
print("§6  Inference demo")
print("=" * 72)

engine = ZRayECGInference(
    model_path=MODEL_PATH,
    device=str(DEVICE),
    scaling_mean=SCALING_MEAN,
    scaling_std=SCALING_STD,
)

# Grab first test sample
demo_signal = X_test_np[0:1]  # already scaled, but inference class re-scales from raw
demo_raw    = (demo_signal * SCALING_STD.reshape(1, 12, 1) +
               SCALING_MEAN.reshape(1, 12, 1))  # un-scale back to raw for demo
label, conf, probs = engine.predict(demo_raw)
print(f"  Prediction : {label}")
print(f"  Confidence : {conf:.1f}%")
print(f"  All probs  : {probs}")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §7  ONNX EXPORT & INT8 QUANTIZATION                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§7  ONNX export & INT8 quantization …")
print("=" * 72)

import onnx
import onnxruntime as ort

# ── 7.1  Export FP32 ONNX ─────────────────────────────────────────────────────
fp32_path = os.path.join(ONNX_DIR, "zray_ecg_fp32.onnx")

# Build a clean inference model (dropout=0.0 for export)
export_model = ECGResNet1D(in_channels=12, num_classes=5, dropout=0.0)
export_model.load_state_dict(best_model_wts)
export_model.eval()

dummy_input = torch.randn(1, 12, 1000)

torch.onnx.export(
    export_model,
    dummy_input,
    fp32_path,
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    input_names=["ecg_input"],
    output_names=["logits"],
    dynamic_axes={
        "ecg_input": {0: "batch_size"},
        "logits":    {0: "batch_size"},
    },
)

# Validate the exported model
onnx_model = onnx.load(fp32_path)
onnx.checker.check_model(onnx_model)
fp32_size = os.path.getsize(fp32_path) / (1024 * 1024)
print(f"  ✓ FP32 ONNX exported: {fp32_path} ({fp32_size:.2f} MB)")

# ── 7.2  INT8 dynamic quantization ───────────────────────────────────────────
from onnxruntime.quantization import quantize_dynamic, QuantType

int8_path     = os.path.join(ONNX_DIR, "zray_ecg_int8.onnx")
preproc_path  = os.path.join(ONNX_DIR, "zray_ecg_fp32_preproc.onnx")

try:
    # Run shape inference / pre-processing to prevent quantization errors
    from onnxruntime.quantization import quant_pre_process
    quant_pre_process(fp32_path, preproc_path)
    source_for_quant = preproc_path
    print("  ✓ quant_pre_process completed")
except Exception as e:
    print(f"  ⚠ quant_pre_process skipped ({e}), using raw FP32 model")
    source_for_quant = fp32_path

try:
    quantize_dynamic(
        model_input=source_for_quant,
        model_output=int8_path,
        weight_type=QuantType.QInt8,
    )
    int8_size = os.path.getsize(int8_path) / (1024 * 1024)
    print(f"  ✓ INT8 ONNX exported: {int8_path} ({int8_size:.2f} MB)")
    print(f"  ↳ Size reduction: {fp32_size:.2f} MB → {int8_size:.2f} MB "
          f"({(1 - int8_size / fp32_size) * 100:.1f}% smaller)")
except Exception as e:
    print(f"  ✗ INT8 quantization failed: {e}")
    int8_path = None

# ── 7.3  Validate with ONNX Runtime ──────────────────────────────────────────
print("\n  Validating ONNX inference …")
for tag, path in [("FP32", fp32_path), ("INT8", int8_path)]:
    if path is None or not os.path.exists(path):
        continue
    sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    ort_input = {sess.get_inputs()[0].name: dummy_input.numpy()}
    ort_out   = sess.run(None, ort_input)[0]
    print(f"  {tag} output shape: {ort_out.shape}  sample: {ort_out[0, :3]}")

# Clean up the preprocessing artefact
if os.path.exists(preproc_path):
    os.remove(preproc_path)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §8  FINAL SUMMARY                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§8  Run Summary")
print("=" * 72)

final_auc = history["val_auc"][-1] if history["val_auc"] else 0.0
final_acc = history["val_acc"][-1] if history["val_acc"] else 0.0

print(f"""
┌────────────────────────────────────────────────────────────┐
│  ZRay ECG — PTB-XL Training Complete                      │
├────────────────────────────────────────────────────────────┤
│  Best Val Loss   : {best_val_loss:.4f}                            │
│  Final Val Acc   : {final_acc:.4f}                            │
│  Final Val AUC   : {final_auc:.4f}                            │
├────────────────────────────────────────────────────────────┤
│  Saved Artifacts:                                         │
│    Model    : {MODEL_PATH}              │
│    Plots    : {PLOT_DIR}/              │
│    ONNX FP32: {fp32_path}              │
│    ONNX INT8: {int8_path or "N/A"}              │
└────────────────────────────────────────────────────────────┘
""")

print("[DONE] Script finished successfully.")
