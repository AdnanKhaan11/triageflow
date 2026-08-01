import pickle
import numpy as np


class SeverityScorer:
    SEVERITY_LABELS = ["low", "medium", "high", "critical"]

    def __init__(self, model_path: str):
        with open(model_path, "rb") as f:
            data = pickle.load(f)
        self.model = data["model"]
        self.feat_cols = data["feature_cols"]

    def predict(self, features: np.ndarray) -> str:
        idx = self.model.predict(features.reshape(1, -1))[0]
        return self.SEVERITY_LABELS[int(idx)]

    def predict_proba(self, features: np.ndarray) -> dict:
        proba = self.model.predict_proba(features.reshape(1, -1))[0]
        return dict(zip(self.SEVERITY_LABELS, proba.tolist()))
