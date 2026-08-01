from pathlib import Path

# ------------------------------------------------------------------
# Root project directory (triageflow already exists)
# ------------------------------------------------------------------
ROOT = Path(__file__).parent

if not ROOT.exists():
    raise FileNotFoundError(f"Project directory '{ROOT}' does not exist.")

# ------------------------------------------------------------------
# Directories to create
# ------------------------------------------------------------------
directories = [
    ROOT / "predictive",
    ROOT / "predictive" / "models",
    ROOT / "predictive" / "saved_models",
]

for directory in directories:
    directory.mkdir(parents=True, exist_ok=True)
    print(f"✓ Directory: {directory}")

# ------------------------------------------------------------------
# Files to create
# ------------------------------------------------------------------
files = {
    ROOT / "predictive" / "__init__.py": "",
    ROOT / "predictive" / "pipeline.py": "",
    ROOT / "predictive" / "monitor.py": "",
    ROOT / "predictive" / "requirements.txt": "",
    ROOT / "predictive" / "models" / "__init__.py": "",
    ROOT / "predictive" / "models" / "feature_extractor.py": "",
    ROOT / "predictive" / "models" / "anomaly_detector.py": "",
    ROOT / "predictive" / "models" / "fault_classifier.py": "",
    ROOT / "predictive" / "models" / "rul_predictor.py": "",
    ROOT / "predictive" / "models" / "severity_scorer.py": "",
    ROOT / "predictive" / "saved_models" / "cwru_fault_classifier.pt": "",
    ROOT / "predictive" / "saved_models" / "anomaly_detector_supervised.pt": "",
    ROOT / "predictive" / "saved_models" / "rul_cnn_bilstm.pt": "",
    ROOT / "predictive" / "saved_models" / "severity_xgboost.pkl": "",
}

# ------------------------------------------------------------------
# Create files if they don't exist
# ------------------------------------------------------------------
for file_path, content in files.items():
    if not file_path.exists():
        file_path.write_text(content, encoding="utf-8")
        print(f"✓ Created: {file_path}")
    else:
        print(f"• Already exists: {file_path}")

print("\n🎉 Predictive module structure created successfully.")
