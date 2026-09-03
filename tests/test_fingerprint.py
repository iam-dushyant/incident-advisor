from src.advisor.firestore_store import IncidentStore

def test_same_incident_same_fingerprint():
    e={"service":"api","resource_name":"orders-api"}
    a=IncidentStore.fingerprint("SERVICE_5XX_SPIKE",e)
    b=IncidentStore.fingerprint("SERVICE_5XX_SPIKE",e)
    assert a==b