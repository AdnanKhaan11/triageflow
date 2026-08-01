"""
predictive/pipeline.py

Complete inference pipeline: raw sensor signal -> TriageFlow ticket.

MODELS USED:
    anomaly_detector_supervised.pt  - AUC 0.9991 (supervised 1D-CNN)
    cwru_fault_classifier.pt        - 97.68% accuracy (2D-CNN + TTA)
    rul_cnn_bilstm.pt               - RMSE 17.8 cycles (CNN-BiLSTM)
    severity_xgboost.pkl            - 98.0% accuracy (XGBoost)
"""

from __future__ import annotations

import pickle
import numpy as np
import torch
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# ── Model architecture imports ────────────────────────────────
from predictive.models.feature_extractor import UniversalFeatureExtractor
from predictive.models.anomaly_detector import AnomalyClassifier1DCNN
from predictive.models.fault_classifier import FaultClassifierCNN
from predictive.models.rul_predictor import RULPredictor
from predictive.models.severity_scorer import SeverityScorer

# ── Model file paths ──────────────────────────────────────────
# All models live in predictive/saved_models/
# Change MODELS_DIR if you put them somewhere else.
MODELS_DIR = Path(__file__).parent / "saved_models"

ANOMALY_MODEL_FILE = "anomaly_detector_supervised.pt"
CWRU_MODEL_FILE = "cwru_fault_classifier.pt"
RUL_MODEL_FILE = "rul_cnn_bilstm.pt"
SEVERITY_MODEL_FILE = "severity_xgboost.pkl"

# ── Constants ─────────────────────────────────────────────────
WINDOW_SIZE = 2048  # anomaly detector window (samples)
CWRU_CLASSES = [
    "Ball_007",
    "Ball_014",
    "Ball_021",
    "IR_007",
    "IR_014",
    "IR_021",
    "Normal",
    "OR_007",
    "OR_014",
    "OR_021",
]

USEFUL_SENSORS = [
    "sensor_2",
    "sensor_3",
    "sensor_4",
    "sensor_7",
    "sensor_8",
    "sensor_9",
    "sensor_11",
    "sensor_12",
    "sensor_13",
    "sensor_14",
    "sensor_15",
    "sensor_17",
    "sensor_20",
    "sensor_21",
]


@dataclass
class PredictionResult:
    equipment_id: str
    is_anomaly: bool
    anomaly_probability: float
    fault_type: str
    fault_confidence: float
    severity: str
    rms: float
    kurtosis: float
    peak_to_peak: float
    anomaly_threshold: float
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)

    def is_critical(self) -> bool:
        return self.severity == "critical"


class TriageFlowPipeline:
    """
    Loads all 4 trained models and runs complete inference on a
    raw vibration signal, returning a structured prediction ready
    for the TriageFlow API.

    Usage:
        pipeline = TriageFlowPipeline()
        result   = pipeline.predict(signal, equipment_id="P-204")
        ticket   = pipeline.generate_ticket_text(result)
    """

    def __init__(
        self,
        models_dir: str | Path = MODELS_DIR,
        verbose: bool = True,
    ) -> None:
        self.models_dir = Path(models_dir)
        self.verbose = verbose
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.extractor = UniversalFeatureExtractor()
        self._verify_model_files()
        self._load_all_models()
        if self.verbose:
            print(f"TriageFlowPipeline ready on {self.device}")
            print(f"Models directory: {self.models_dir.resolve()}")

    def _verify_model_files(self) -> None:
        """Check all required model files exist before loading."""
        required = [
            ANOMALY_MODEL_FILE,
            CWRU_MODEL_FILE,
            RUL_MODEL_FILE,
            SEVERITY_MODEL_FILE,
        ]
        missing = []
        for fname in required:
            fpath = self.models_dir / fname
            if not fpath.exists():
                missing.append(str(fpath))

        if missing:
            raise FileNotFoundError(
                "Missing model files:\n"
                + "\n".join(f"  - {f}" for f in missing)
                + f"\n\nPlace these files in: {self.models_dir.resolve()}"
            )

    def _load_all_models(self) -> None:
        """Load all 4 models from saved_models/ directory."""

        # ── 1. Anomaly Detector ───────────────────────────────
        ckpt_ae = torch.load(
            self.models_dir / ANOMALY_MODEL_FILE,
            map_location=self.device,
            weights_only=False,
        )
        self.anomaly_model = AnomalyClassifier1DCNN(
            window_size=ckpt_ae.get("window_size", WINDOW_SIZE)
        ).to(self.device)
        self.anomaly_model.load_state_dict(ckpt_ae["model_state"])
        self.anomaly_model.eval()
        self.anomaly_threshold = float(ckpt_ae["threshold"])

        if self.verbose:
            print(
                f"  [1/4] Anomaly detector loaded  "
                f"(threshold={self.anomaly_threshold:.4f})"
            )

        # ── 2. CWRU Fault Classifier ──────────────────────────
        ckpt_cwru = torch.load(
            self.models_dir / CWRU_MODEL_FILE,
            map_location=self.device,
            weights_only=False,
        )
        self.class_names = ckpt_cwru.get("class_names", CWRU_CLASSES)
        self.fault_model = FaultClassifierCNN(n_classes=len(self.class_names)).to(
            self.device
        )
        self.fault_model.load_state_dict(ckpt_cwru["model_state"])
        self.fault_model.eval()

        if self.verbose:
            print(
                f"  [2/4] Fault classifier loaded  "
                f"({len(self.class_names)} classes)"
            )

        # ── 3. RUL Predictor ──────────────────────────────────
        ckpt_rul = torch.load(
            self.models_dir / RUL_MODEL_FILE,
            map_location=self.device,
            weights_only=False,
        )
        self.rul_model = RULPredictor(n_features=len(USEFUL_SENSORS)).to(self.device)
        self.rul_model.load_state_dict(ckpt_rul["model_state"])
        self.rul_model.eval()
        self.max_rul = int(ckpt_rul.get("max_rul", 125))

        if self.verbose:
            val_rmse = ckpt_rul.get("val_rmse", "N/A")
            print(
                f"  [3/4] RUL predictor loaded     " f"(val_rmse={val_rmse:.2f} cycles)"
            )

        # ── 4. XGBoost Severity Scorer ────────────────────────
        self.severity_scorer = SeverityScorer(
            str(self.models_dir / SEVERITY_MODEL_FILE)
        )

        if self.verbose:
            print(f"  [4/4] Severity scorer loaded")

    def predict(
        self,
        signal: np.ndarray,
        equipment_id: str = "P-204",
        sampling_rate: int = 20480,
        tta_augments: int = 5,
    ) -> PredictionResult:
        """
        Run complete inference on a raw vibration signal.

        Args:
            signal:        1D numpy array of vibration readings
            equipment_id:  Equipment ID (e.g. "P-204", "C-11", "M-18")
            sampling_rate: Sensor sampling rate in Hz
            tta_augments:  Number of test-time augmentations for
                           fault classifier (more = slightly better,
                           but slower)

        Returns:
            PredictionResult with all predictions
        """
        signal = signal.flatten().astype(np.float32)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # ── Step 1: Extract statistical features ─────────────
        features = self.extractor.extract(signal, sampling_rate)

        # ── Step 2: Anomaly detection ─────────────────────────
        window = (
            signal[:WINDOW_SIZE]
            if len(signal) >= WINDOW_SIZE
            else np.pad(signal, (0, WINDOW_SIZE - len(signal)))
        )
        window_norm = (window - window.mean()) / (window.std() + 1e-8)
        window_t = torch.FloatTensor(window_norm).unsqueeze(0).to(self.device)

        with torch.no_grad():
            anomaly_prob = float(
                torch.softmax(self.anomaly_model(window_t), dim=1)[0, 1]
            )
        is_anomaly = anomaly_prob > self.anomaly_threshold

        # ── Step 3: Fault classification (with TTA) ───────────
        seg = (
            signal[:1024]
            if len(signal) >= 1024
            else np.pad(signal, (0, 1024 - len(signal)))
        )
        spec = np.abs(seg.reshape(32, 32)).astype(np.float32)
        spec = (spec - spec.mean()) / (spec.std() + 1e-8)

        # TTA: average predictions over multiple augmented versions
        all_probs = np.zeros(len(self.class_names))
        for aug_idx in range(tta_augments):
            spec_aug = spec.copy()
            if aug_idx > 0:
                spec_aug += np.random.randn(*spec_aug.shape) * 0.03

            spec_t = torch.FloatTensor(spec_aug[np.newaxis, np.newaxis]).to(self.device)
            with torch.no_grad():
                logits = self.fault_model(spec_t)
                probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
            all_probs += probs

        all_probs /= tta_augments
        fault_type = self.class_names[int(np.argmax(all_probs))]
        fault_conf = float(np.max(all_probs))

        # Not an anomaly → override to Normal
        if not is_anomaly:
            fault_type = "Normal"
            fault_conf = 1.0

        # ── Step 4: Severity scoring ──────────────────────────
        severity = self.severity_scorer.predict(features)
        if not is_anomaly:
            severity = "low"

        return PredictionResult(
            equipment_id=equipment_id,
            is_anomaly=is_anomaly,
            anomaly_probability=round(anomaly_prob, 4),
            fault_type=fault_type,
            fault_confidence=round(fault_conf, 4),
            severity=severity,
            rms=round(float(features[0]), 4),
            kurtosis=round(float(features[3]), 4),
            peak_to_peak=round(float(features[2]), 4),
            anomaly_threshold=round(self.anomaly_threshold, 4),
            timestamp=ts,
        )

    def generate_ticket_text(
        self,
        result: PredictionResult,
    ) -> str:
        """Format a PredictionResult as a TriageFlow ticket."""
        sev = result.severity.upper()
        status = "ANOMALY DETECTED" if result.is_anomaly else "NORMAL"
        ratio = (
            result.anomaly_probability / result.anomaly_threshold
            if result.anomaly_threshold > 0
            else 0
        )

        return f"""AUTOMATED SENSOR ALERT — {result.equipment_id}

Timestamp: {result.timestamp}
Equipment ID: {result.equipment_id}
Detected Fault Type: {result.fault_type} \
(confidence: {result.fault_confidence:.1%})
Estimated Severity: {sev}

Anomaly Detection:
  Status:              {status}
  Anomaly Probability: {result.anomaly_probability:.4f}
  Threshold:           {result.anomaly_threshold:.4f}
  Ratio to Threshold:  {ratio:.2f}x

Sensor Readings at Detection:
  RMS Vibration:   {result.rms:.4f}
  Kurtosis:        {result.kurtosis:.4f}
  Peak-to-Peak:    {result.peak_to_peak:.4f}

This ticket was automatically generated by the TriageFlow
Predictive Maintenance System. The AI pipeline has classified
this as a {result.fault_type} fault with {sev} severity.
Human supervisor review is required before any maintenance
action is taken."""
