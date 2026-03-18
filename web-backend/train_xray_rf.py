import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier

# Setup paths to ensure files drop exactly where FastAPI expects them
BASE_DIR = os.getcwd() 
SAVE_DIR = os.path.join(BASE_DIR, "deployment", "fusion_assets")
os.makedirs(SAVE_DIR, exist_ok=True)

print("🚨 INITIALIZING Z-RAY FUSION TRAINING...")

# ==========================================
# 1. ECG FUSION ENGINE (5 Classes)
# ==========================================
print("\n⚙️ Training ECG Clinical Reasoner...")
# Inputs: 5 AI Probs + Age + Gender + Prev_Diag = 8 Features
samples = 2000
X_ai_ecg = np.random.dirichlet(np.ones(5), size=samples)
age_ecg = np.random.randint(18, 90, samples)
gender_ecg = np.random.randint(0, 2, samples)
prev_ecg = np.random.randint(0, 2, samples)

X_ecg = np.column_stack((X_ai_ecg, age_ecg, gender_ecg, prev_ecg))
y_ecg = np.argmax(X_ai_ecg, axis=1)

# Clinical Bias Rules
for i in range(samples):
    if y_ecg[i] == 0 and age_ecg[i] > 65 and prev_ecg[i] == 1:
        if np.random.rand() > 0.4: y_ecg[i] = 3 # Bias to Conduction Disturbance
    elif y_ecg[i] == 1 and gender_ecg[i] == 1 and age_ecg[i] > 50:
        pass # Confirm MI
    elif age_ecg[i] < 30 and prev_ecg[i] == 0:
        if np.random.rand() > 0.6: y_ecg[i] = 0 # Bias to Normal

rf_ecg = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
rf_ecg.fit(X_ecg, y_ecg)

ecg_path = os.path.join(SAVE_DIR, "ecg_fusion.joblib")
joblib.dump(rf_ecg, ecg_path)
print(f"✅ ECG Fusion saved to: {ecg_path}")

# ==========================================
# 2. X-RAY FUSION ENGINE (2 Classes: Normal vs Pneumonia)
# ==========================================
print("\n⚙️ Training X-Ray Clinical Reasoner...")
# Inputs: 2 AI Probs + Age + Gender + Prev_Diag = 5 Features
X_ai_xray = np.random.dirichlet(np.ones(2), size=samples)
age_xray = np.random.randint(5, 90, samples)
gender_xray = np.random.randint(0, 2, samples)
prev_xray = np.random.randint(0, 2, samples)

X_xray = np.column_stack((X_ai_xray, age_xray, gender_xray, prev_xray))
y_xray = np.argmax(X_ai_xray, axis=1)

# Clinical Bias Rules
for i in range(samples):
    # If AI is borderline (prob > 40%) but patient is old or has history -> Bias to Pneumonia
    if X_ai_xray[i][1] > 0.40 and (age_xray[i] > 65 or prev_xray[i] == 1):
        y_xray[i] = 1
    # If AI suspects Pneumonia but patient is young/healthy -> Slight chance to override to Normal
    elif y_xray[i] == 1 and age_xray[i] < 30 and prev_xray[i] == 0:
        if np.random.rand() > 0.8: y_xray[i] = 0 

rf_xray = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
rf_xray.fit(X_xray, y_xray)

xray_path = os.path.join(SAVE_DIR, "xray_fusion.joblib")
joblib.dump(rf_xray, xray_path)
print(f"✅ X-Ray Fusion saved to: {xray_path}")

print("\n🎉 ALL CLINICAL REASONERS SUCCESSFULLY COMPILED!")