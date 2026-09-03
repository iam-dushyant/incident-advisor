from src.advisor.inference import IncidentModel

def test_permission_denied():
    m=IncidentModel("artifacts/model/incident_classifier.joblib",0.50)
    p=m.predict({
        "severity":"ERROR","service":"iam","status_code":403,
        "resource_name":"projects/x/secrets/y",
        "message":"403 PERMISSION_DENIED service account lacks secretmanager.versions.access"
    })
    assert p.incident_id=="IAM_PERMISSION_DENIED"