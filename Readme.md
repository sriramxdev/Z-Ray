# Z-Ray: Tri-Modal Medical Diagnostic Engine 🩺

[![Hackathon](https://img.shields.io/badge/Hackathon-UHack%204.0-blueviolet)](https://github.com/Zeta-Coders/Z-Ray)
[![Tech Stack](https://img.shields.io/badge/Tech-PyTorch%20%7C%20FastAPI%20%7C%20Vite-orange)](https://github.com/Zeta-Coders/Z-Ray)
[![Model Optimization](https://img.shields.io/badge/Optimization-INT8%20Quantization%20%7C%20ONNX-green)](https://github.com/Zeta-Coders/Z-Ray)

**Z-Ray** is a high-performance, multi-modal AI diagnostic suite developed by **Zeta Coders**. It integrates X-Ray, MRI, and ECG analysis into a unified "Glass-Box" dashboard, providing clinicians with high-accuracy predictions backed by visual heatmaps and clinical fusion.

---

## 🚀 Core Engine Architecture

Z-Ray utilizes three distinct specialized engines to provide a 360-degree diagnostic view:

### 1. Vision Engine (Chest X-Ray)
* **Backbone:** MobileNetV3-Large (Optimized for edge deployment).
* **Dataset:** NIH Chest X-ray 14 (112,120 clinical images).
* **Feature:** **Grad-CAM Explainability** – Heatmaps that highlight exactly where the AI detects pathologies like Atelectasis or Pneumonia, ensuring clinical trust.

### 2. Volumetric Engine (Knee MRI)
* **Strategy:** **2.5D Spatial Stacking** – Processes 3D MRI slices as multi-channel inputs to capture structural depth without the computational cost of 3D CNNs.
* **Hybrid Reasoning:** Combines AI vision probabilities with patient clinical data (pain level, swelling) using a **Random Forest Fusion** model.

### 3. Signal Engine (12-Lead ECG)
* **Architecture:** 1D-Residual Network (1D-ResNet).
* **Dataset:** PTB-XL Clinical Dataset (100Hz signals).
* **Optimization:** **OneCycleLR Scheduling** – Reaches 90%+ diagnostic accuracy through dynamic learning rate adjustment.

---

## 🛠️ Systems Engineering & Optimization

As a project designed for real-world utility on constrained devices (like a **Redmi Note 7 Pro**), Z-Ray employs advanced optimization techniques:

* **INT8 Quantization:** Models are compressed from FP32 to INT8, reducing file sizes by ~75% while maintaining >98% of original accuracy.
* **ONNX Runtime:** Unified cross-platform inference that allows the backend to run on non-dGPU hardware (Ryzen 5 6600H) with millisecond latency.
* **FOSS Priority:** Built entirely using Free and Open Source Software (Fedora, PyTorch, MONAI, FastAPI).

---

## 📂 Project Structure

```text
Z-Ray/
├── models/
│   ├── xray/          # MobileNetV3 + Grad-CAM Logic
│   ├── ecg/           # 1D-ResNet Signal Processor
│   └── mri/           # 2.5D Stacking + Fusion Engine
├── deployment/
│   └── onnx_assets/   # INT8 Quantized Production Models
├── web-backend/       # FastAPI Gateway (Unified Inference API)
└── web-frontend/      # Vite + React Dashboard (Zeta-UI)
