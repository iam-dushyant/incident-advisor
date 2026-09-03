from __future__ import annotations
import hashlib
from google.cloud import firestore

class IncidentStore:
    def __init__(self):
        self.db = firestore.Client()

    @staticmethod
    def fingerprint(incident_type: str, event: dict) -> str:
        raw = '|'.join([
            incident_type,
            str(event.get('service', 'unknown')),
            str(event.get('resource_name', 'unknown')),
        ])
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    def upsert(self, prediction, event: dict, runbook: dict) -> str:
        fp = self.fingerprint(prediction.incident_type, event)
        ref = self.db.collection('incidents').document(fp)
        snap = ref.get()
        now = firestore.SERVER_TIMESTAMP

        payload = {
            'incident_type': prediction.incident_type,
            'confidence': prediction.confidence,
            'service': event.get('service'),
            'resource': event.get('resource_name'),
            'last_seen': now,
            'latest_message': event.get('message'),
            'suggested_steps': runbook.get('steps', []),
            'status': 'OPEN' if prediction.incident_type != 'HEALTHY' else 'IGNORED',
        }
        if snap.exists:
            payload["event_count"] = firestore.Increment(1)
        else:
            payload["event_count"] = 1
            payload["first_seen"] = now
        ref.set(payload, merge=True)
        return fp