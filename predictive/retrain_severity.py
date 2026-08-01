"""
predictive/retrain_severity.py
Retrains the XGBoost severity scorer locally so it's
compatible with your installed XGBoost version.
Run: python -m predictive.retrain_severity
"""

import numpy as np
import pandas as pd
import pickle
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from pathlib import Path

print("Retraining XGBoost severity scorer locally...")
print(f"XGBoost version: {xgb.__version__}")

FEAT_COLS = [
    "rms",
    "peak",
    "peak_to_peak",
    "kurtosis",
    "skewness",
    "crest_factor",
    "std",
    "variance",
    "dominant_freq",
    "spectral_energy",
    "spectral_entropy",
    "spectral_mean",
    "spectral_std",
]
SEVERITY_ORDER = ["low", "medium", "high", "critical"]
SEVERITY_ENC = {s: i for i, s in enumerate(SEVERITY_ORDER)}
N_SAMPLES = 6000
np.random.seed(42)

# ── Generate synthetic training data ─────────────────────────
# This mimics the feature distributions we observed in training
records = []

for _ in range(N_SAMPLES):
    label = np.random.choice(
        ["low", "medium", "high", "critical"], p=[0.45, 0.35, 0.12, 0.08]
    )
    if label == "low":
        rms = np.random.uniform(0.03, 0.08)
        kurt = np.random.uniform(-0.5, 2.0)
        peak = rms * np.random.uniform(3, 5)
    elif label == "medium":
        rms = np.random.uniform(0.08, 0.18)
        kurt = np.random.uniform(1.5, 5.0)
        peak = rms * np.random.uniform(4, 7)
    elif label == "high":
        rms = np.random.uniform(0.15, 0.28)
        kurt = np.random.uniform(4.0, 9.0)
        peak = rms * np.random.uniform(5, 9)
    else:  # critical
        rms = np.random.uniform(0.25, 0.50)
        kurt = np.random.uniform(8.0, 20.0)
        peak = rms * np.random.uniform(7, 12)

    p2p = peak * 2 * np.random.uniform(0.9, 1.1)
    crest = peak / (rms + 1e-8)
    std = rms * np.random.uniform(0.95, 1.05)
    skew = np.random.normal(0, 0.5)
    variance = std**2
    dom_freq = np.random.uniform(50, 500)
    sp_energy = np.random.uniform(1e5, 1e8)
    sp_ent = np.random.uniform(6, 12)
    sp_mean = np.random.uniform(2000, 8000)
    sp_std = np.random.uniform(1000, 4000)

    records.append(
        {
            "rms": rms,
            "peak": peak,
            "peak_to_peak": p2p,
            "kurtosis": kurt,
            "skewness": skew,
            "crest_factor": crest,
            "std": std,
            "variance": variance,
            "dominant_freq": dom_freq,
            "spectral_energy": sp_energy,
            "spectral_entropy": sp_ent,
            "spectral_mean": sp_mean,
            "spectral_std": sp_std,
            "label": label,
        }
    )

df = pd.DataFrame(records)
df["severity_enc"] = df["label"].map(SEVERITY_ENC)

X = df[FEAT_COLS].values.astype(np.float32)
y = df["severity_enc"].values

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)
X_tr, X_v, y_tr, y_v = train_test_split(
    X_tr, y_tr, test_size=0.15, stratify=y_tr, random_state=42
)

print(f"Train: {len(X_tr)} | Val: {len(X_v)} | Test: {len(X_te)}")

model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss",
    early_stopping_rounds=20,
    random_state=42,
    device="cpu",  # force CPU so it works everywhere
)

model.fit(
    X_tr,
    y_tr,
    eval_set=[(X_v, y_v)],
    verbose=50,
)

y_pred = model.predict(X_te)
test_acc = (y_pred == y_te).mean()
print(f"\nTest accuracy: {test_acc:.4f}")
print(classification_report(y_te, y_pred, target_names=SEVERITY_ORDER))

# Save
save_path = Path(__file__).parent / "saved_models" / "severity_xgboost.pkl"
save_path.parent.mkdir(parents=True, exist_ok=True)
with open(save_path, "wb") as f:
    pickle.dump(
        {
            "model": model,
            "severity_order": SEVERITY_ORDER,
            "severity_enc": SEVERITY_ENC,
            "feature_cols": FEAT_COLS,
        },
        f,
    )

print(f"\nSaved to: {save_path}")
print("Now run: python -m predictive.monitor ...")
