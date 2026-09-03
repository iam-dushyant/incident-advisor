from __future__ import annotations
from dataclasses import dataclass
import joblib

@dataclass
class Prediction:
    incident_id: str
    confidence: float

class IncidentModel:
    def __init__(self, model_path: str, unknown_threshold: float = 0.62):
        self.model = joblib.load(model_path)
        self.threshold = unknown_threshold

    def predict(self, event: str) -> Prediction:
        text = (
            f"severity={event.get('severity', '')} "
            f"service={event.get('service', '')} "
            f"status={event.get('status_code', '')} "
            f"resource={event.get('resource_name', '')}"
            f"{event.get('message', '')}"
        )
        probs = self.model.predict_proba([text])[0]
        idx = int(probs.argmax())
        label = str(self.model.classes_[idx])
        confidence = float(probs[idx])
        if confidence < self.threshold:
            return Prediction("UNKNOWN", confidence=confidence)
        return Prediction(label, confidence=confidence)