# Cell 1: Setup
!pip install -q monai pydicom opencv-python-headless onnx onnxruntime
import os
import warnings
import gc
import glob
import traceback

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
warnings.filterwarnings("ignore")

print("Z-Ray Environment Setup Complete & Warnings Silenced.")
# Cell 2: Dataset
import cv2
import torch
import pydicom
import numpy as np
from torch.utils.data import Dataset, DataLoader
from monai.transforms import Compose, Resize, RandRotate, RandZoom, ToTensor

class ZRayVisionDataset(Dataset):
    def __init__(self, image_paths, labels, is_training=True):
        self.image_paths = image_paths
        self.labels = labels
        self.is_training = is_training
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        self.image_size = 224
        
        if is_training:
            self.transform = Compose([
                Resize((self.image_size, self.image_size)),
                RandRotate(range_x=0.15, prob=0.5, keep_size=True),
                RandZoom(min_zoom=0.9, max_zoom=1.1, prob=0.5, keep_size=True),
                ToTensor()
            ])
        else:
            self.transform = Compose([
                Resize((self.image_size, self.image_size)),
                ToTensor()
            ])

    def _load_and_process_image(self, path):
        try:
            if path.lower().endswith('.dcm'):
                img = pydicom.dcmread(path).pixel_array
            else:
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                raise IOError(f"Failed to load image: {path}")

            if img.dtype != np.uint8:
                img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            
            img_clahe = self.clahe.apply(img)
            img_rgb = cv2.cvtColor(img_clahe, cv2.COLOR_GRAY2RGB)
            return np.transpose(img_rgb, (2, 0, 1)).astype(np.float32) / 255.0
        except Exception as e:
            print(f"Error processing file {path}: {e}")
            img_rgb = np.zeros((self.image_size, self.image_size, 3), dtype=np.uint8)
            return np.transpose(img_rgb, (2, 0, 1)).astype(np.float32) / 255.0

    def __getitem__(self, idx):
        img_array = self._load_and_process_image(self.image_paths[idx])
        img_tensor = self.transform(img_array)
        return img_tensor, torch.tensor(self.labels[idx], dtype=torch.float32)

    def __len__(self): 
        return len(self.image_paths)

print("✅ Vision Dataset Updated with robust transforms.")
# Cell 3: Model Definition
import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights

class ZRayVisionModel(nn.Module):
    def __init__(self, num_classes=15, dropout_rate=0.3):
        super(ZRayVisionModel, self).__init__()
        
        weights = MobileNet_V3_Large_Weights.DEFAULT
        self.backbone = mobilenet_v3_large(weights=weights)
        
        # Freeze early layers
        for param in list(self.backbone.features[:7].parameters()):
            param.requires_grad = False
            
        self.features = self.backbone.features
        
        in_features = self.backbone.classifier[0].in_features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(512, num_classes)
        )
        
        # Grad-CAM storage
        self.gradients = None
        self.activations = None

    def activations_hook(self, grad):
        self.gradients = grad

    def forward(self, x):
        x = self.features(x)
        self.activations = x
        
        # Only register hook if we need gradients (training or Grad-CAM)
        if self.training or torch.is_grad_enabled():
            if x.requires_grad:
                x.register_hook(self.activations_hook)
        
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
        
    def get_activations_gradient(self):
        return self.gradients
    
    def get_activations(self, x):
        return self.features(x)
# Cell 3: Model Definition
import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_large, MobileNet_V3_Large_Weights

class ZRayVisionModel(nn.Module):
    def __init__(self, num_classes=15, dropout_rate=0.3):
        super(ZRayVisionModel, self).__init__()
        
        weights = MobileNet_V3_Large_Weights.DEFAULT
        self.backbone = mobilenet_v3_large(weights=weights)
        
        # Freeze early layers
        for param in list(self.backbone.features[:7].parameters()):
            param.requires_grad = False
            
        self.features = self.backbone.features
        
        in_features = self.backbone.classifier[0].in_features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(512, num_classes)
        )
        
        # Grad-CAM storage
        self.gradients = None
        self.activations = None

    def activations_hook(self, grad):
        self.gradients = grad

    def forward(self, x):
        x = self.features(x)
        self.activations = x
        
        # Only register hook if we need gradients (training or Grad-CAM)
        if self.training or torch.is_grad_enabled():
            if x.requires_grad:
                x.register_hook(self.activations_hook)
        
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
        
    def get_activations_gradient(self):
        return self.gradients
    
    def get_activations(self, x):
        return self.features(x)
# Cell 4: Training Utilities
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import numpy as np
import torch.optim as optim
from torch.cuda.amp import autocast, GradScaler
from torch.optim.lr_scheduler import ReduceLROnPlateau
from tqdm import tqdm

def calculate_accuracy(preds, targets, threshold=0.5):
    preds_binary = (torch.sigmoid(preds) > threshold).float()
    correct = (preds_binary == targets).all(dim=1).sum().item()
    return correct / targets.size(0)

print("✅ Training utilities loaded.")
# Cell 5: Visualization Functions
def plot_training_curves(history):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 6))
    epochs_range = range(1, len(history['train_loss']) + 1)
    
    ax1.plot(epochs_range, history['train_loss'], label='Training Loss', color='blue', marker='o', linestyle='-')
    ax1.plot(epochs_range, history['val_loss'], label='Validation Loss', color='red', marker='s', linestyle='--')
    ax1.set_title('Z-Ray: Training vs Validation Loss', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('BCEWithLogits Loss')
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    ax2.plot(epochs_range, history['train_acc'], label='Training Accuracy', color='green', marker='o', linestyle='-')
    ax2.plot(epochs_range, history['val_acc'], label='Validation Accuracy', color='orange', marker='s', linestyle='--')
    ax2.set_title('Z-Ray: Training vs Validation Accuracy', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Epochs')
    ax2.set_ylabel('Accuracy')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig('/kaggle/working/training_curves.png', dpi=300, bbox_inches='tight')
    plt.show()

def evaluate_and_plot_roc(model, val_loader, device, mlb_classes):
    print("🔬 Generating ROC-AUC Graph...")
    model.eval()
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for images, labels in tqdm(val_loader, desc="Calculating ROC"):
            images = images.to(device)
            with autocast():
                preds = torch.sigmoid(model(images))
            all_preds.append(preds.cpu().numpy())
            all_targets.append(labels.cpu().numpy())
            
    all_preds = np.vstack(all_preds)
    all_targets = np.vstack(all_targets)
    
    plt.figure(figsize=(14, 10))
    
    class_frequencies = all_targets.sum(axis=0)
    if 'No Finding' in mlb_classes:
        no_finding_idx = list(mlb_classes).index('No Finding')
        class_frequencies[no_finding_idx] = -1
        
    top_8_indices = np.argsort(class_frequencies)[-8:]
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    
    for i, class_idx in enumerate(top_8_indices):
        fpr, tpr, _ = roc_curve(all_targets[:, class_idx], all_preds[:, class_idx])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, color=colors[i], lw=2, label=f'{mlb_classes[class_idx]} (AUC = {roc_auc:.3f})')
        
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Guess')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Z-Ray Model ROC-AUC for Top 8 Pathologies', fontsize=18, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.5)
    plt.savefig('/kaggle/working/roc_curve.png', dpi=300, bbox_inches='tight')
    plt.show()
# Cell 6: Grad-CAM Functions
def generate_gradcam(model, image_tensor, class_idx, device):
    model.eval()
    image_tensor = image_tensor.to(device)
    
    # Enable gradients for Grad-CAM
    with torch.enable_grad():
        output = model(image_tensor)
        model.zero_grad()
        target = output[0, class_idx]
        target.backward()
    
    actual_model = model.module if isinstance(model, nn.DataParallel) else model
    gradients = actual_model.get_activations_gradient()
    activations = actual_model.activations
    
    if gradients is None or activations is None:
        print("Warning: Gradients or activations not found.")
        return None
        
    pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])
    
    for i in range(activations.size(1)):
        activations[:, i, :, :] *= pooled_gradients[i]
        
    heatmap = torch.mean(activations, dim=1).squeeze()
    heatmap = torch.maximum(heatmap, torch.tensor(0.0, device=heatmap.device))
    heatmap /= (torch.max(heatmap) + 1e-8)
    
    return heatmap.detach().cpu().numpy()

def visualize_zray_result(img_path, heatmap, alpha=0.6):
    if heatmap is None:
        return
        
    image_size = 224
    original_img = cv2.imread(img_path)
    if original_img is None:
        print(f"Could not load image: {img_path}")
        return
        
    original_img = cv2.resize(original_img, (image_size, image_size))
    heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
    
    heatmap_colored = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)
    superimposed_img = cv2.addWeighted(heatmap_colored, alpha, original_img, 1 - alpha, 0)
    
    fig, ax = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Z-Ray Explainability (Grad-CAM)", fontsize=20, fontweight='bold')

    ax[0].imshow(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB))
    ax[0].set_title('Original X-Ray')
    ax[0].axis('off')
    
    ax[1].imshow(heatmap_colored)
    ax[1].set_title('AI Attention Heatmap')
    ax[1].axis('off')
    
    ax[2].imshow(cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB))
    ax[2].set_title('Clinical Verification Overlay')
    ax[2].axis('off')
    
    plt.tight_layout()
    plt.savefig('/kaggle/working/grad_cam_example.png', dpi=300, bbox_inches='tight')
    plt.show()

print("✅ Grad-CAM pipeline ready.")
# Cell 7: Export Functions
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType

def export_to_edge(model, device, image_size=224):
    print("\n📦 Initiating Edge Export Pipeline...")
    
    model.to('cpu').eval()
    dummy_input = torch.randn(1, 3, image_size, image_size)
    
    actual_model = model.module if isinstance(model, nn.DataParallel) else model
    
    fp32_path = "/kaggle/working/zray_vision_fp32.onnx"
    int8_path = "/kaggle/working/zray_vision_int8.onnx"
    
    print("Step 1/3: Exporting to ONNX FP32 format...")
    try:
        torch.onnx.export(
            actual_model,
            dummy_input,
            fp32_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
        )
        print("✅ ONNX FP32 export successful.")
    except Exception as e:
        print(f"❌ ONNX FP32 export failed: {e}")
        return

    print("Step 2/3: Applying INT8 dynamic quantization...")
    try:
        quantize_dynamic(
            model_input=fp32_path,
            model_output=int8_path,
            weight_type=QuantType.QInt8
        )
        print("✅ INT8 quantization successful.")
    except Exception as e:
        print(f"❌ INT8 quantization failed: {e}")
        return

    if os.path.exists(fp32_path) and os.path.exists(int8_path):
        fp32_size = os.path.getsize(fp32_path) / (1024 * 1024)
        int8_size = os.path.getsize(int8_path) / (1024 * 1024)
        compression_ratio = (1 - int8_size / fp32_size) * 100
        
        print("\n" + "="*40)
        print("🚀 Z-Ray Edge Export Complete!")
        print("="*40)
        print(f"🔹 Original ONNX (FP32) Size: {fp32_size:.2f} MB")
        print(f"🔹 Quantized ONNX (INT8) Size: {int8_size:.2f} MB")
        print(f"🔹 Compression Achieved: {compression_ratio:.2f}%")
        print("="*40)
    else:
        print("❌ Final model files not found.")

print("✅ Export functions ready.")
# Cell 8: Main Training Loop (Fixed with robust path handling)
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split

# Clear memory
torch.cuda.empty_cache()
gc.collect()
print("✅ Memory cleared.")

# Load and prepare data with robust path handling
print("\n🔄 Loading and preparing data...")
try:
    # First, let's see what's in the input directory
    print("Scanning for dataset files...")
    all_files = glob.glob('/kaggle/input/**/*', recursive=True)
    print(f"Found {len(all_files)} total files in input directory")
    
    # Try multiple possible CSV locations
    possible_csv_paths = [
        '/kaggle/input/**/Data_Entry_2017.csv',
        '/kaggle/input/**/**/Data_Entry_2017.csv',
        '/kaggle/input/data/Data_Entry_2017.csv',
        '/kaggle/input/chest-xray-data/Data_Entry_2017.csv',
        '/kaggle/input/nih-chest-xrays/Data_Entry_2017.csv'
    ]
    
    csv_path = None
    for pattern in possible_csv_paths:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            csv_path = matches[0]
            print(f"✅ Found CSV at: {csv_path}")
            break
    
    if csv_path is None:
        # If still not found, list all CSV files
        csv_files = glob.glob('/kaggle/input/**/*.csv', recursive=True)
        print(f"Available CSV files: {csv_files}")
        if csv_files:
            csv_path = csv_files[0]
            print(f"Using: {csv_path}")
        else:
            raise FileNotFoundError("No CSV files found in the input directory")
    
    df = pd.read_csv(csv_path)
    print(f"CSV loaded with {len(df)} rows")
    
    # Find image paths
    print("Scanning for image files...")
    all_image_paths = glob.glob('/kaggle/input/**/*.png', recursive=True)
    if not all_image_paths:
        all_image_paths = glob.glob('/kaggle/input/**/*.jpg', recursive=True)
    if not all_image_paths:
        all_image_paths = glob.glob('/kaggle/input/**/*.jpeg', recursive=True)
    
    print(f"Found {len(all_image_paths)} image files")
    
    if len(all_image_paths) == 0:
        raise FileNotFoundError("No image files found in the input directory")
    
    # Create path dictionary
    path_dict = {}
    for p in all_image_paths:
        basename = os.path.basename(p)
        if basename not in path_dict:  # Keep first occurrence
            path_dict[basename] = p
    
    print(f"Created path dictionary with {len(path_dict)} unique image names")
    
    # Map paths to dataframe
    df['full_path'] = df['Image Index'].map(path_dict)
    
    # Check mapping success rate
    mapped_count = df['full_path'].notna().sum()
    print(f"Successfully mapped {mapped_count}/{len(df)} images ({mapped_count/len(df)*100:.1f}%)")
    
    # Drop unmapped rows
    df.dropna(subset=['full_path'], inplace=True)
    
    if len(df) == 0:
        raise ValueError("No images could be mapped. Check if image filenames match CSV entries.")
    
    # Process labels
    df['Finding Labels'] = df['Finding Labels'].apply(lambda x: x.split('|'))
    
    mlb = MultiLabelBinarizer()
    labels_matrix = mlb.fit_transform(df['Finding Labels'])
    class_names = mlb.classes_
    print(f"Found {len(class_names)} classes: {list(class_names)}")
    
    # Use a smaller subset for faster testing (remove for full training)
    # Uncomment below for testing with smaller dataset
    # sample_size = min(5000, len(df))
    # df = df.sample(n=sample_size, random_state=42)
    # labels_matrix = labels_matrix[df.index]
    
    # Split data
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        df['full_path'].values, labels_matrix, test_size=0.1, random_state=42
    )
    print(f"Train samples: {len(train_paths)}, Val samples: {len(val_paths)}")
    print("✅ Data preparation complete!")
    
except Exception as e:
    print(f"❌ Error in data loading: {e}")
    traceback.print_exc()
    # Create dummy data for testing if real data fails
    print("\n⚠️ Creating dummy data for testing...")
    class_names = np.array(['Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema', 
                           'Effusion', 'Emphysema', 'Fibrosis', 'Hernia', 
                           'Infiltration', 'Mass', 'No Finding', 'Nodule', 
                           'Pleural_Thickening', 'Pneumonia', 'Pneumothorax'])
    num_samples = 100
    train_paths = ['/kaggle/input/dummy'] * int(num_samples * 0.9)
    val_paths = ['/kaggle/input/dummy'] * int(num_samples * 0.1)
    train_labels = np.random.randint(0, 2, (len(train_paths), len(class_names)))
    val_labels = np.random.randint(0, 2, (len(val_paths), len(class_names)))
    print("✅ Dummy data created for testing")

# Create datasets and dataloaders
BATCH_SIZE = 32  # Reduced for stability
NUM_WORKERS = 0   # Set to 0 to avoid worker crashes

print("\n📦 Creating datasets...")
train_dataset = ZRayVisionDataset(train_paths, train_labels, is_training=True)
val_dataset = ZRayVisionDataset(val_paths, val_labels, is_training=False)

train_loader = DataLoader(
    train_dataset, 
    batch_size=BATCH_SIZE, 
    shuffle=True, 
    num_workers=NUM_WORKERS, 
    pin_memory=True if NUM_WORKERS > 0 else False
)

val_loader = DataLoader(
    val_dataset, 
    batch_size=BATCH_SIZE, 
    shuffle=False, 
    num_workers=NUM_WORKERS, 
    pin_memory=True if NUM_WORKERS > 0 else False
)
print(f"✅ DataLoaders configured. Batch: {BATCH_SIZE} | Train batches: {len(train_loader)} | Val batches: {len(val_loader)}")

# Setup model
print("\n🤖 Setting up model...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

model = ZRayVisionModel(num_classes=len(class_names))

# Test model with dummy input
try:
    dummy_input = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        dummy_output = model(dummy_input)
    print(f"✅ Model test passed. Output shape: {dummy_output.shape}")
except Exception as e:
    print(f"❌ Model test failed: {e}")
    traceback.print_exc()

# Multi-GPU setup
if torch.cuda.device_count() > 1:
    print(f"🚀 Accelerating with {torch.cuda.device_count()} GPUs!")
    model = nn.DataParallel(model)

model = model.to(device)
print(f"Model moved to {device}")

# Training function
def train_model(train_loader, val_loader, epochs=5):
    print("\n🚀 Starting training...")
    
    optimizer = optim.AdamW(model.parameters(), lr=5e-4, weight_decay=1e-5)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.2, patience=2)
    scaler = GradScaler()
    
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    best_val_loss = float('inf')
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        train_acc = 0.0
        
        loop = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
        for batch_idx, (images, labels) in enumerate(loop):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            
            with autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)
            
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            train_loss += loss.item()
            train_acc += calculate_accuracy(outputs, labels)
            
            loop.set_postfix(loss=loss.item())
            
            # Clear cache occasionally
            if batch_idx % 50 == 0:
                torch.cuda.empty_cache()
        
        avg_train_loss = train_loss / len(train_loader)
        avg_train_acc = train_acc / len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_acc = 0.0
        
        with torch.no_grad():
            val_loop = tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Val]")
            for images, labels in val_loop:
                images, labels = images.to(device), labels.to(device)
                
                with autocast():
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                val_acc += calculate_accuracy(outputs, labels)
        
        avg_val_loss = val_loss / len(val_loader)
        avg_val_acc = val_acc / len(val_loader)
        
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['train_acc'].append(avg_train_acc)
        history['val_acc'].append(avg_val_acc)
        
        print(f"\nEpoch {epoch+1} Results:")
        print(f"  Train Loss: {avg_train_loss:.4f} | Train Acc: {avg_train_acc:.4f}")
        print(f"  Val Loss: {avg_val_loss:.4f} | Val Acc: {avg_val_acc:.4f}")
        
        scheduler.step(avg_val_loss)
        
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            model_to_save = model.module if isinstance(model, nn.DataParallel) else model
            torch.save(model_to_save.state_dict(), "/kaggle/working/zray_best_model.pth")
            print(f"  ✨ New best model saved! (Val Loss: {best_val_loss:.4f})")
        
        # Clean up
        torch.cuda.empty_cache()
        gc.collect()
    
    return history

# Train the model
try:
    print("\n" + "="*50)
    print("STARTING TRAINING")
    print("="*50)
    
    history = train_model(train_loader, val_loader, epochs=5)  # Adjust epochs as needed
    
    # Plot results
    print("\n📊 Generating training curves...")
    plot_training_curves(history)
    
    print("\n📈 Generating ROC curves...")
    evaluate_and_plot_roc(model, val_loader, device, class_names)
    
    # Save and export
    best_model_path = "/kaggle/working/zray_best_model.pth"
    if os.path.exists(best_model_path):
        print("\n💾 Saving final models...")
        final_model = ZRayVisionModel(num_classes=len(class_names))
        final_model.load_state_dict(torch.load(best_model_path, map_location='cpu'))
        
        # Save PyTorch model
        torch.save(final_model.state_dict(), "/kaggle/working/zray_model_final.pth")
        print("✅ PyTorch model saved to /kaggle/working/zray_model_final.pth")
        
        # Export to ONNX
        export_to_edge(final_model, device)
        
        print("\n" + "="*50)
        print("🎉 TRAINING COMPLETE! 🎉")
        print("="*50)
        print("\nGenerated files:")
        print("  - PyTorch model: /kaggle/working/zray_model_final.pth")
        print("  - Best model: /kaggle/working/zray_best_model.pth")
        print("  - ONNX FP32: /kaggle/working/zray_vision_fp32.onnx")
        print("  - ONNX INT8: /kaggle/working/zray_vision_int8.onnx")
        print("  - Training curves: /kaggle/working/training_curves.png")
        print("  - ROC curve: /kaggle/working/roc_curve.png")
        
except Exception as e:
    print(f"❌ Training error: {e}")
    traceback.print_exc()
# Cell 9: Grad-CAM Visualization (Optional - Run after training)
print("\n🩺 Generating Grad-CAM visualizations...")

if os.path.exists("/kaggle/working/zray_best_model.pth"):
    # Load the best model
    final_model = ZRayVisionModel(num_classes=len(class_names))
    final_model.load_state_dict(torch.load("/kaggle/working/zray_best_model.pth", map_location='cpu'))
    final_model = final_model.to(device)
    
    # Get sample images
    num_visualizations = 3
    sample_indices = np.random.choice(len(val_dataset), min(num_visualizations, len(val_dataset)), replace=False)
    
    for i in sample_indices:
        image_tensor, label = val_dataset[i]
        image_tensor = image_tensor.unsqueeze(0)
        image_path = val_dataset.image_paths[i]
        
        # Get predictions
        with torch.no_grad():
            output = final_model(image_tensor.to(device))
            probabilities = torch.sigmoid(output).cpu().numpy().flatten()
        
        predicted_class_idx = np.argmax(probabilities)
        predicted_class_name = class_names[predicted_class_idx]
        predicted_confidence = probabilities[predicted_class_idx]
        
        print(f"\n--- Visualizing: {os.path.basename(image_path)} ---")
        print(f"Top Prediction: '{predicted_class_name}' (Confidence: {predicted_confidence:.2f})")
        
        heatmap = generate_gradcam(final_model, image_tensor, predicted_class_idx, device)
        visualize_zray_result(image_path, heatmap)
else:
    print("❌ No trained model found. Train the model first.")
