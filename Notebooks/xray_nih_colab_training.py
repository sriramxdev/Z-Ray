# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §0  COLAB SETUP (Run this cell first!)                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# !pip install -q kaggle onnx onnxruntime onnxscript

# ── 1. Setup Kaggle API Credentials ───────────────────────────────────────────
# Uncomment and insert your Kaggle username and key
# import os
# os.environ['KAGGLE_USERNAME'] = "YOUR_KAGGLE_USERNAME"
# os.environ['KAGGLE_KEY'] = "YOUR_KAGGLE_KEY"

# ── 2. Download Dataset ───────────────────────────────────────────────────────
# Note: The NIH Chest X-Ray 14 dataset is very large (~40GB). 
# Uncomment the following line to download and unzip it directly into Colab's /content/dataset
# # !kaggle datasets download -d nih-chest-xrays/data -p /content/dataset --unzip


#!/usr/bin/env python3
"""
================================================================================
 ZRay Vision — NIH Chest X-Ray 14 Multi-Label Classification (DenseNet-121)
 -------------------------------------------------------------------------
 Production-ready training script for Kaggle notebooks.
 Trains a custom DenseNet-121 wrapper on the NIH Chest X-ray 14 dataset,
 generates presentation-quality visualizations, and exports the model to
 an edge-optimized ONNX format with INT8 dynamic quantization.

 Classes (15): Atelectasis · Cardiomegaly · Effusion · Infiltration ·
               Mass · Nodule · Pneumonia · Pneumothorax · Consolidation ·
               Edema · Emphysema · Fibrosis · Pleural_Thickening ·
               Hernia · No Finding

 Target metric: macro-AUC  |  Export: ONNX opset-14 (FP32 + INT8)
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
        importable = pkg.split("==")[0].split("[")[0]
        try:
            __import__(importable)
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

_pip_install("onnx", "onnxruntime", "onnxscript", "tqdm")

import os
import gc
import ast
import time
import copy
import warnings
from collections import OrderedDict

import numpy as np
import pandas as pd
from PIL import Image
from tqdm.auto import tqdm

import matplotlib
# matplotlib.use("Agg")                       # non-interactive backend for Kaggle
import matplotlib.pyplot as plt
import seaborn as sns

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import autocast, GradScaler

import torchvision.transforms as T
import torchvision.models as models

from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import GroupShuffleSplit

warnings.filterwarnings("ignore")

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIGURATION — change these paths as needed                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ── Dataset root (Kaggle "Add Input" mounts here) ────────────────────────────
# Change this single variable if your mount path differs.
DATASET_ROOT = "/content/dataset"
# Note: Assuming data was unzipped to /content/dataset

# ── Output paths ──────────────────────────────────────────────────────────────
OUTPUT_DIR = "/content/working"
PLOT_DIR   = os.path.join(OUTPUT_DIR, "training_plots")
ONNX_DIR   = os.path.join(OUTPUT_DIR, "deployment", "onnx_assets")
MODEL_PATH = os.path.join(OUTPUT_DIR, "best_xray_model.pth")

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
IMG_SIZE      = 224
BATCH_SIZE    = 64
NUM_WORKERS   = 4
NUM_EPOCHS    = 25
LEARNING_RATE = 1e-3
WEIGHT_DECAY  = 1e-4
PATIENCE      = 7          # early-stopping patience
NUM_CLASSES   = 15

# The 14 pathologies + No Finding, in alphabetical order for consistency
CLASS_NAMES = [
    "Atelectasis", "Cardiomegaly", "Consolidation", "Edema",
    "Effusion", "Emphysema", "Fibrosis", "Hernia",
    "Infiltration", "Mass", "No Finding", "Nodule",
    "Pleural_Thickening", "Pneumonia", "Pneumothorax",
]

# ImageNet normalization statistics
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §2  DATASET LOADING & PREPROCESSING                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§2  Loading NIH Chest X-Ray 14 dataset …")
print("=" * 72)

# ── 2.1  Load CSV metadata ───────────────────────────────────────────────────
csv_path = os.path.join(DATASET_ROOT, "Data_Entry_2017.csv")
df = pd.read_csv(csv_path)
print(f"[INFO] Total entries in CSV: {len(df)}")

# ── 2.2  Parse multi-labels ──────────────────────────────────────────────────
# 'Finding Labels' column has pipe-separated labels, e.g. "Effusion|Infiltration"
df["label_list"] = df["Finding Labels"].apply(lambda x: x.split("|"))

mlb = MultiLabelBinarizer(classes=CLASS_NAMES)
labels_np = mlb.fit_transform(df["label_list"])              # shape (N, 15)
print(f"[INFO] Label matrix shape: {labels_np.shape}")
print(f"[INFO] Classes: {CLASS_NAMES}")

# Add binary columns back to DataFrame for reference
for i, cls in enumerate(CLASS_NAMES):
    df[cls] = labels_np[:, i]

# ── 2.3  Resolve image file paths ────────────────────────────────────────────
# NIH dataset has images scattered in sub-folders (images_001/ … images_012/)
# or sometimes all in a single "images/" folder.  We build a lookup dict.
print("[INFO] Scanning for image files …")
image_lookup = {}
for root, dirs, files in os.walk(DATASET_ROOT):
    for fname in files:
        if fname.lower().endswith(".png"):
            image_lookup[fname] = os.path.join(root, fname)

print(f"[INFO] Found {len(image_lookup):,} PNG images on disk.")

# Filter DataFrame to only rows whose images actually exist
df["image_path"] = df["Image Index"].map(image_lookup)
before = len(df)
df = df.dropna(subset=["image_path"]).reset_index(drop=True)
labels_np = labels_np[df.index] if len(df) < before else labels_np
# Rebuild labels_np after potential filtering
labels_np = np.array([list(row) for row in zip(*[df[cls] for cls in CLASS_NAMES])],
                     dtype=np.float32).T  # (N, 15) — transposed to match
# Actually, let's rebuild cleanly
labels_np = df[CLASS_NAMES].values.astype(np.float32)

print(f"[INFO] Records with existing images: {len(df)}")

# ── 2.4  Patient-aware train/val split (80/20) ───────────────────────────────
# GroupShuffleSplit ensures NO patient overlap between train and val sets.
print("[INFO] Splitting by Patient ID (no overlap) …")
gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=SEED)
groups = df["Patient ID"].values

train_idx, val_idx = next(gss.split(X=df, y=labels_np, groups=groups))
print(f"[INFO] Train: {len(train_idx):,}  |  Val: {len(val_idx):,}")

# ── 2.5  Transforms ──────────────────────────────────────────────────────────
train_transforms = T.Compose([
    T.Resize((IMG_SIZE, IMG_SIZE)),
    T.RandomHorizontalFlip(p=0.5),
    T.RandomRotation(degrees=10),
    T.ColorJitter(brightness=0.1, contrast=0.1),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

val_transforms = T.Compose([
    T.Resize((IMG_SIZE, IMG_SIZE)),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
])

# ── 2.6  Custom Dataset class ────────────────────────────────────────────────
class ChestXrayDataset(Dataset):
    """
    Lazy-loading dataset for NIH Chest X-ray 14.
    Reads images from disk on-the-fly and applies transforms.
    Converts grayscale → RGB by duplicating channels.
    """

    def __init__(self, dataframe, label_array, transform=None):
        self.df        = dataframe.reset_index(drop=True)
        self.labels    = label_array
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_path = self.df.loc[idx, "image_path"]
        label    = self.labels[idx]

        # Load image → ensure RGB (some X-rays are 'L' mode / grayscale)
        img = Image.open(img_path)
        if img.mode != "RGB":
            img = img.convert("RGB")

        if self.transform:
            img = self.transform(img)

        return img, torch.tensor(label, dtype=torch.float32)


# ── 2.7  DataLoaders ─────────────────────────────────────────────────────────
train_ds = ChestXrayDataset(
    df.iloc[train_idx], labels_np[train_idx], transform=train_transforms
)
val_ds = ChestXrayDataset(
    df.iloc[val_idx], labels_np[val_idx], transform=val_transforms
)

train_loader = DataLoader(
    train_ds, batch_size=BATCH_SIZE, shuffle=True,
    num_workers=NUM_WORKERS, pin_memory=True, drop_last=True,
)
val_loader = DataLoader(
    val_ds, batch_size=BATCH_SIZE, shuffle=False,
    num_workers=NUM_WORKERS, pin_memory=True,
)

print(f"[INFO] DataLoaders ready  (train batches: {len(train_loader)}, "
      f"val batches: {len(val_loader)})\n")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §3  MODEL ARCHITECTURE — DenseNet-121 Wrapper                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class ChestXrayDenseNet(nn.Module):
    """
    Custom DenseNet-121 wrapper for multi-label Chest X-Ray classification.

    Architecture:
        DenseNet-121 features → ReLU → AdaptiveAvgPool2d(1) →
        flatten (ONNX-safe) → Dropout → Linear(1024, 15)

    Training from scratch (no pretrained weights) as we are specializing
    on medical X-ray imagery.
    """

    def __init__(self, num_classes=15, dropout=0.3):
        super().__init__()

        # Load DenseNet-121 WITHOUT pretrained weights
        base = models.densenet121(weights=None)

        # Extract the feature-extraction backbone (everything except the classifier)
        self.features = base.features          # returns (B, 1024, H', W')
        self.relu     = nn.ReLU(inplace=True)
        self.pool     = nn.AdaptiveAvgPool2d(1)
        self.drop     = nn.Dropout(p=dropout)

        # Custom classifier head → 15 logits
        self.classifier = nn.Linear(1024, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = self.relu(x)
        x = self.pool(x)
        # ── CRITICAL: use torch.flatten for stable ONNX export ────────
        x = torch.flatten(x, 1)               # (B, 1024)
        x = self.drop(x)
        x = self.classifier(x)                 # (B, 15)
        return x


# ── Instantiate ──────────────────────────────────────────────────────────────
model = ChestXrayDenseNet(num_classes=NUM_CLASSES, dropout=0.3).to(DEVICE)
total_params = sum(p.numel() for p in model.parameters())
print(f"[MODEL] ChestXrayDenseNet (DenseNet-121) — {total_params:,} parameters\n")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §4  TRAINING LOOP & OPTIMIZATION                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("=" * 72)
print("§4  Training with Mixed Precision …")
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

# ── AMP scaler for mixed-precision training ──────────────────────────────────
scaler = GradScaler(enabled=(DEVICE.type == "cuda"))

# ── Metric history ────────────────────────────────────────────────────────────
history = {
    "train_loss": [], "val_loss": [],
    "val_auc":    [],
}

best_val_auc   = 0.0
best_model_wts = copy.deepcopy(model.state_dict())
epochs_no_improve = 0


for epoch in range(1, NUM_EPOCHS + 1):
    t0 = time.time()

    # ── Training phase ────────────────────────────────────────────────────
    model.train()
    running_loss = 0.0
    n_batches    = 0

    pbar = tqdm(train_loader, desc=f"Epoch {epoch:02d}/{NUM_EPOCHS} [TRAIN]",
                leave=False, dynamic_ncols=True)
    for xb, yb in pbar:
        xb, yb = xb.to(DEVICE, non_blocking=True), yb.to(DEVICE, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)

        # Mixed precision forward pass
        with autocast(enabled=(DEVICE.type == "cuda")):
            logits = model(xb)
            loss   = criterion(logits, yb)

        # Scaled backward pass
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()

        running_loss += loss.item()
        n_batches    += 1
        pbar.set_postfix(loss=f"{loss.item():.4f}",
                         lr=f"{scheduler.get_last_lr()[0]:.2e}")

    train_loss = running_loss / max(n_batches, 1)

    # ── Validation phase ──────────────────────────────────────────────────
    model.eval()
    val_loss_sum, val_n = 0.0, 0
    all_val_logits, all_val_labels = [], []

    pbar = tqdm(val_loader, desc=f"Epoch {epoch:02d}/{NUM_EPOCHS} [VAL]  ",
                leave=False, dynamic_ncols=True)
    with torch.no_grad():
        for xb, yb in pbar:
            xb, yb = xb.to(DEVICE, non_blocking=True), yb.to(DEVICE, non_blocking=True)

            with autocast(enabled=(DEVICE.type == "cuda")):
                logits = model(xb)
                loss   = criterion(logits, yb)

            val_loss_sum += loss.item()
            val_n        += 1

            all_val_logits.append(logits.float().cpu())
            all_val_labels.append(yb.cpu())

    val_loss = val_loss_sum / max(val_n, 1)

    # ── Compute macro AUC ─────────────────────────────────────────────────
    all_val_logits = torch.cat(all_val_logits).numpy()
    all_val_labels = torch.cat(all_val_labels).numpy()
    all_val_probs  = 1.0 / (1.0 + np.exp(-all_val_logits))   # sigmoid

    try:
        val_auc = roc_auc_score(
            all_val_labels, all_val_probs, average="macro", multi_class="ovr"
        )
    except ValueError:
        # Can happen if a class has zero positive samples in this split
        per_class_aucs = []
        for i in range(NUM_CLASSES):
            if all_val_labels[:, i].sum() > 0:
                per_class_aucs.append(
                    roc_auc_score(all_val_labels[:, i], all_val_probs[:, i])
                )
        val_auc = np.mean(per_class_aucs) if per_class_aucs else 0.0

    elapsed = time.time() - t0

    # ── Logging ───────────────────────────────────────────────────────────
    history["train_loss"].append(train_loss)
    history["val_loss"].append(val_loss)
    history["val_auc"].append(val_auc)

    print(
        f"Epoch {epoch:02d}/{NUM_EPOCHS} │ "
        f"train_loss {train_loss:.4f} │ "
        f"val_loss {val_loss:.4f} │ "
        f"val_AUC {val_auc:.4f} │ "
        f"lr {scheduler.get_last_lr()[0]:.2e} │ "
        f"{elapsed:.1f}s"
    )

    # ── Early stopping (based on AUC — higher is better) ──────────────────
    if val_auc > best_val_auc:
        best_val_auc   = val_auc
        best_model_wts = copy.deepcopy(model.state_dict())
        epochs_no_improve = 0
        torch.save(best_model_wts, MODEL_PATH)
        print(f"  ↳ Best model saved (AUC = {val_auc:.4f})")
    else:
        epochs_no_improve += 1
        if epochs_no_improve >= PATIENCE:
            print(f"\n[EARLY STOP] No AUC improvement for {PATIENCE} epochs.")
            break

    # ── Memory cleanup ────────────────────────────────────────────────────
    del all_val_logits, all_val_labels, all_val_probs
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# Restore best weights
model.load_state_dict(best_model_wts)
print(f"\n[INFO] Training complete.  Best val AUC: {best_val_auc:.4f}")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §5  PRESENTATION VISUALIZATIONS                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§5  Generating presentation visualizations …")
print("=" * 72)

sns.set_theme(style="whitegrid", font_scale=1.15)
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
print("  ✓ Saved loss_curves.png")

# ── 5.2  Full test-set inference for ROC & bar chart ──────────────────────────
print("  Running final validation pass for ROC curves …")
model.eval()
final_logits, final_labels = [], []
with torch.no_grad():
    for xb, yb in tqdm(val_loader, desc="Final val inference", leave=False):
        xb = xb.to(DEVICE, non_blocking=True)
        with autocast(enabled=(DEVICE.type == "cuda")):
            logits = model(xb)
        final_logits.append(logits.float().cpu())
        final_labels.append(yb)

final_logits = torch.cat(final_logits).numpy()
final_labels = torch.cat(final_labels).numpy()
final_probs  = 1.0 / (1.0 + np.exp(-final_logits))

# ── 5.3  ROC-AUC curves (all 15 classes) ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 8))
colors = sns.color_palette("husl", NUM_CLASSES)
per_class_auc = {}

for i, cls_name in enumerate(CLASS_NAMES):
    if final_labels[:, i].sum() == 0:
        per_class_auc[cls_name] = float("nan")
        continue
    fpr, tpr, _ = roc_curve(final_labels[:, i], final_probs[:, i])
    auc_val = roc_auc_score(final_labels[:, i], final_probs[:, i])
    per_class_auc[cls_name] = auc_val
    ax.plot(fpr, tpr, color=colors[i], linewidth=1.5,
            label=f"{cls_name} ({auc_val:.3f})")

ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC-AUC Curves — 15 Classes (NIH Chest X-Ray 14)")
ax.legend(loc="lower right", fontsize=8, ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "roc_auc_curves.png"), dpi=200)
plt.close(fig)
print("  ✓ Saved roc_auc_curves.png")

# ── 5.4  Class-wise AUC bar chart ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
auc_series = pd.Series(per_class_auc).dropna().sort_values(ascending=True)
bars = ax.barh(auc_series.index, auc_series.values, color=sns.color_palette("viridis", len(auc_series)))
ax.set_xlabel("AUC Score")
ax.set_title("Per-Class Validation AUC — NIH Chest X-Ray 14")
ax.set_xlim(0, 1.0)

# Annotate bars with AUC values
for bar, val in zip(bars, auc_series.values):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", fontsize=9)

fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "classwise_auc_bar.png"), dpi=200)
plt.close(fig)
print("  ✓ Saved classwise_auc_bar.png")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §6  PRODUCTION INFERENCE INTERFACE                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class ZRayVisionInference:
    """
    Clean inference class for multi-label Chest X-Ray classification.

    Usage:
        engine = ZRayVisionInference("best_xray_model.pth", device="cpu")
        label, confidence, probs = engine.predict(tensor_1x3x224x224)

    Parameters
    ----------
    model_path : str
        Path to the saved `best_xray_model.pth` state dict.
    device : str
        PyTorch device string ("cpu" or "cuda").
    """

    CLASS_NAMES = [
        "Atelectasis", "Cardiomegaly", "Consolidation", "Edema",
        "Effusion", "Emphysema", "Fibrosis", "Hernia",
        "Infiltration", "Mass", "No Finding", "Nodule",
        "Pleural_Thickening", "Pneumonia", "Pneumothorax",
    ]

    def __init__(self, model_path, device="cpu"):
        self.device = torch.device(device)

        # Build model with dropout=0 for deterministic inference
        self.model = ChestXrayDenseNet(num_classes=15, dropout=0.0)
        state = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, tensor_input):
        """
        Run inference on a single normalized Chest X-Ray tensor.

        Parameters
        ----------
        tensor_input : torch.Tensor, shape (1, 3, 224, 224)
            Already resized, RGB, and ImageNet-normalized.

        Returns
        -------
        top_label   : str     — Highest-probability class name.
        confidence  : float   — Confidence percentage (0–100).
        all_probs   : dict    — {class_name: probability} for all 15 classes.
        """
        assert tensor_input.shape == (1, 3, IMG_SIZE, IMG_SIZE), \
            f"Expected (1, 3, {IMG_SIZE}, {IMG_SIZE}), got {tensor_input.shape}"

        tensor_input = tensor_input.to(self.device)
        with torch.no_grad():
            logits = self.model(tensor_input)
        probs = torch.sigmoid(logits).cpu().numpy().squeeze()

        top_idx    = int(np.argmax(probs))
        top_label  = self.CLASS_NAMES[top_idx]
        confidence = float(probs[top_idx]) * 100.0
        all_probs  = {name: float(p) for name, p in zip(self.CLASS_NAMES, probs)}

        return top_label, confidence, all_probs


# ── Quick inference demo ──────────────────────────────────────────────────────
print("\n" + "=" * 72)
print("§6  Inference demo")
print("=" * 72)

engine = ZRayVisionInference(model_path=MODEL_PATH, device=str(DEVICE))

# Use first validation sample as a demo
demo_img, demo_lbl = val_ds[0]
demo_input = demo_img.unsqueeze(0)                           # (1, 3, 224, 224)
label, conf, probs = engine.predict(demo_input)
print(f"  Prediction : {label}")
print(f"  Confidence : {conf:.1f}%")
print(f"  All probs  : { {k: round(v, 4) for k, v in probs.items()} }")


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §7  ONNX EXPORT & INT8 QUANTIZATION                                      ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§7  ONNX export & INT8 quantization …")
print("=" * 72)

import onnx
import onnxruntime as ort

# ── 7.1  Export FP32 ONNX ─────────────────────────────────────────────────────
fp32_path = os.path.join(ONNX_DIR, "zray_xray_fp32.onnx")

# Build a clean export model (dropout=0.0)
export_model = ChestXrayDenseNet(num_classes=NUM_CLASSES, dropout=0.0)
export_model.load_state_dict(best_model_wts)
export_model.eval()

dummy_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE)

torch.onnx.export(
    export_model,
    dummy_input,
    fp32_path,
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    input_names=["xray_input"],
    output_names=["logits"],
    dynamic_axes={
        "xray_input": {0: "batch_size"},
        "logits":     {0: "batch_size"},
    },
)

# Validate
onnx_model = onnx.load(fp32_path)
onnx.checker.check_model(onnx_model)
fp32_size = os.path.getsize(fp32_path) / (1024 * 1024)
print(f"  ✓ FP32 ONNX exported: {fp32_path} ({fp32_size:.2f} MB)")

# ── 7.2  INT8 dynamic quantization ───────────────────────────────────────────
from onnxruntime.quantization import quantize_dynamic, QuantType

int8_path    = os.path.join(ONNX_DIR, "zray_xray_int8.onnx")
preproc_path = os.path.join(ONNX_DIR, "zray_xray_fp32_preproc.onnx")

# quant_pre_process prevents shape inference errors during quantization
try:
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

# Clean up intermediate preprocessing artefact
if os.path.exists(preproc_path):
    os.remove(preproc_path)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  §8  FINAL SUMMARY                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

print("\n" + "=" * 72)
print("§8  Run Summary")
print("=" * 72)

final_auc = history["val_auc"][-1] if history["val_auc"] else 0.0

print(f"""
┌──────────────────────────────────────────────────────────────────┐
│  ZRay Vision — NIH Chest X-Ray 14 Training Complete             │
├──────────────────────────────────────────────────────────────────┤
│  Best Val AUC    : {best_val_auc:.4f}                                   │
│  Final Val Loss  : {history["val_loss"][-1]:.4f}                                   │
│  Epochs Trained  : {len(history["train_loss"])}                                         │
├──────────────────────────────────────────────────────────────────┤
│  Per-Class AUCs:                                                │""")
for cls, auc in per_class_auc.items():
    auc_str = f"{auc:.4f}" if not np.isnan(auc) else "  N/A "
    print(f"│    {cls:<22s} : {auc_str}                              │")
print(f"""├──────────────────────────────────────────────────────────────────┤
│  Saved Artifacts:                                               │
│    Model    : {MODEL_PATH:<47s} │
│    Plots    : {PLOT_DIR + '/':<47s} │
│    ONNX FP32: {fp32_path:<47s} │
│    ONNX INT8: {(int8_path or 'N/A'):<47s} │
└──────────────────────────────────────────────────────────────────┘
""")

print("[DONE] Script finished successfully.")
