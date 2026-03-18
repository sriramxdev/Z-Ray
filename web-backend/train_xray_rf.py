import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier

SAVE_DIR = os.path.join(os.getcwd(), "deployment", "fusion_assets")
os.makedirs(SAVE_DIR, exist_ok=True)

print("⚙️ Training X-Ray Clinical Reasoner...")
# Generate synthetic data for 2 AI classes (Normal, Pneumonia) + 3 Tabular (Age, Gender, Prev_Diag)
X_ai = np.random.dirichlet(np.ones(2), size=1000)
X_tabular = np.column_stack((np.random.randint(18, 90, 1000), np.random.randint(0, 2, 1000), np.random.randint(0, 2, 1000)))
X_total = np.hstack((X_ai, X_tabular))

# Target Logic: Bias heavily towards the AI's prediction
y = np.argmax(X_ai, axis=1)

model = RandomForestClassifier(n_estimators=50, max_depth=3, random_state=42)
model.fit(X_total, y)

joblib.dump(model, os.path.join(SAVE_DIR, "xray_fusion.joblib"))
print("✅ X-Ray Fusion Engine saved!")