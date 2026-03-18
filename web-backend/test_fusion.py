import numpy as np
import joblib
import os

# 1. Load the Glass-Box Reasoning Function
def generate_ecg_reasoning(signal_probs, age, gender, prev_diag, final_class_idx):
    class_map = {
        0: 'Normal Sinus Rhythm', 1: 'Myocardial Infarction (MI)', 
        2: 'ST/T Wave Changes (STTC)', 3: 'Conduction Disturbance (CD)', 4: 'Hypertrophy (HYP)'
    }
    condition = class_map[final_class_idx]
    base_conf = signal_probs[0][final_class_idx]
    
    reasoning = [f"1. 1D-ResNet Signal Analysis: Morphologic deviations indicative of {condition} (Base AI Confidence: {base_conf*100:.1f}%)."]
    risk_multiplier = 1.0
    
    if gender == 1 and age > 50 and final_class_idx == 1:
        risk_multiplier += 0.18
        reasoning.append(f"2. Demographic Correlation: Male gender over age 50 carries a higher historical incidence rate for acute coronary syndromes.")
    elif age > 65 and final_class_idx in [3, 4]:
        risk_multiplier += 0.15
        reasoning.append(f"2. Demographic Correlation: Advanced age ({age}) strongly correlates with degenerative structural heart changes.")
        
    if prev_diag == 1:
        risk_multiplier += 0.25
        reasoning.append(f"3. Longitudinal Risk Factor: Prior documented cardiovascular events compound the probability.")
    else:
        reasoning.append(f"3. Patient History: No prior cardiac history reported.")
        
    final_conf = min(base_conf * risk_multiplier, 0.99)
    conclusion = f"► Final Clinical Assessment: {condition}. Weighted confidence: {final_conf*100:.1f}%."
    reasoning.append(conclusion)
    return condition, final_conf, reasoning

# 2. Load the actual trained .joblib model
model_path = os.path.join(os.getcwd(), "web-backend", "deployment", "fusion_rf_assets", "ecg_fusion.joblib")
if not os.path.exists(model_path):
    print(f"🔴 ERROR: Model not found at {model_path}")
    exit()

rf_model = joblib.load(model_path)
print("✅ Random Forest Fusion Model Loaded Successfully!\n")

# ==========================================
# 3. TEST SCENARIOS
# ==========================================

# Scenario A: Young, healthy male (Low AI suspicion of anything)
# Features: [Norm, MI, STTC, CD, HYP, Age, Gender(1=M), Prev_Diag(1=Y)]
patient_a_ai_probs = [[0.80, 0.05, 0.05, 0.05, 0.05]]
patient_a_tabular = [25, 1, 0] 
X_a = np.hstack((patient_a_ai_probs, [patient_a_tabular]))

# Scenario B: Older male with history, AI strongly suspects an MI
patient_b_ai_probs = [[0.10, 0.75, 0.05, 0.05, 0.05]]
patient_b_tabular = [68, 1, 1]
X_b = np.hstack((patient_b_ai_probs, [patient_b_tabular]))

# Run Inference
for idx, (patient_name, X_data, raw_ai) in enumerate([("Patient A (25yo, Healthy)", X_a, patient_a_ai_probs), 
                                                      ("Patient B (68yo, Prior History, MI Suspected)", X_b, patient_b_ai_probs)]):
    
    # Predict Class and Probability
    predicted_class = rf_model.predict(X_data)[0]
    fusion_probs = rf_model.predict_proba(X_data)
    
    # Generate the Glass-Box Text
    condition, conf, reasoning = generate_ecg_reasoning(raw_ai, X_data[0][5], X_data[0][6], X_data[0][7], predicted_class)
    
    print(f"🏥 --- {patient_name} ---")
    print(f"Diagnosis: {condition}")
    for step in reasoning:
        print(f"  {step}")
    print("\n")