from __future__ import annotations
import base64, json, logging, os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from .firestore_store import IncidentStore
from .inference import IncidentModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("incident-advisor")

MODEL_PATH = os.environ.get("MODEL_PATH", "artifacts/model/incident_classifier.joblib")
RUNBOOK_PATH = os.environ.get("RUNBOOK_PATH", "runbooks/runbooks.json")

model = IncidentModel(
    MODEL_PATH,
    unknown_threshold = float(os.environ.get("UNKNOWN_THRESHOLD", "0.62"))
)

runbooks = json.loads(Path(RUNBOOK_PATH).read_text())
store = IncidentStore()
app = FastAPI(title="Incident Advisor", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/pubsub")
def pubsub(envelope: dict):
    try:
        encoded = envelope["message"]["data"]
        log_entry = json.loads(base64.b64decode(encoded).decode())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Pub/Sub message: {e}")

    payload = log_entry.get("jsonPayload", {})
    event = {
        "severity": log_entry.get("severity", "DEFAULT"),
        "service": payload.get("service", "unknown"),
        "status_code": payload.get("status_code", 0),
        "resource_name": payload.get("resource_name", "unknown"),
        "message": payload.get("message", log_entry.get("textPayload", "")),
    }

    pred = model.predict(event)
    rb = runbooks.get(pred.incident_type, runbooks["UNKNOWN"])
    fp = store.upsert(pred, event, rb)

    log.info(json.dumps({
        "event": event,
        "fingerprint": fp,
        "incident_type": pred.incident_type,
        "confidence": pred.confidence,
        "service": event["service"],
    }))
    return {"ok": True}