from __future__ import annotations
from dataclasses import dataclass
import random
import uuid

@dataclass(frozen=True)
class Scenario:
    label: str
    severity: str
    service: str
    status_code: int
    templates: tuple[str, ...]

SCENARIOS = [
    Scenario("IAM_PERMISSION_DENIED","ERROR","iam",403,(
        "PermissionDenied: principal {principal} lacks {permission} on {resource}",
        "403 PERMISSION_DENIED for service account {principal} calling {resource}",
        "authorization failed: missing permission {permission} for {principal}",
    )),
    Scenario("QUOTA_OR_RATE_LIMIT","WARNING","compute",429,(
        "429 quota exceeded for {resource}; retry after backoff",
        "rateLimitExceeded: too many requests to {resource}",
        "resource exhausted: quota limit reached for {resource}",
    )),
    Scenario("SERVICE_5XX_SPIKE","ERROR","api",503,(
        "503 upstream service unavailable for request {request_id}",
        "500 internal server error from dependency {resource}",
        "502 bad gateway while calling {resource}",
    )),
    Scenario("LATENCY_SATURATION","WARNING","api",200,(
        "request latency {latency_ms}ms above SLO; concurrency={concurrency}",
        "slow request: latency_ms={latency_ms} cpu={cpu_pct}% concurrency={concurrency}",
    )),
    Scenario("OOM_KILLED","ERROR","gke",137,(
        "container terminated: OOMKilled memory_limit_mb={memory_mb}",
        "pod killed with exit code 137 after exceeding memory limit {memory_mb}MB",
    )),
    Scenario("GKE_CRASHLOOP","ERROR","gke",500,(
        "pod {resource} entered CrashLoopBackOff restart_count={restart_count}",
        "container repeatedly failed startup; pod={resource} restart_count={restart_count}",
    )),
    Scenario("PUBSUB_BACKLOG","WARNING","pubsub",200,(
        "subscription {resource} backlog growing; oldest_unacked_age={age_s}s",
        "subscriber lag detected for {resource}; unacked_messages={unacked}",
    )),
    Scenario("DB_CONNECTION_EXHAUSTION","ERROR","database",500,(
        "connection pool exhausted for {resource}; active={active} max={max_conn}",
        "database refused connection: too many clients for {resource}",
    )),
    Scenario("DNS_RESOLUTION_FAILURE","ERROR","network",500,(
        "DNS resolution failed for {resource}: SERVFAIL",
        "temporary failure in name resolution for host {resource}",
        "NXDOMAIN resolving {resource}",
    )),
    Scenario("HEALTHY","INFO","api",200,(
        "request completed status=200 latency_ms={latency_ms}",
        "health check passed for {resource}",
        "background reconciliation completed successfully",
    )),
]

PRINCIPALS=["svc-api@example.iam.gserviceaccount.com","svc-worker@example.iam.gserviceaccount.com"]
RESOURCES=["projects/demo/secrets/payments","orders-api","inventory-db","sub-orders","api.internal"]
PERMISSIONS=["secretmanager.versions.access","storage.objects.get","pubsub.subscriptions.consume"]

def render(s: Scenario, rng: random.Random) -> dict:
    values = {
        "principal": rng.choice(PRINCIPALS),
        "resource": rng.choice(RESOURCES),
        "permission": rng.choice(PERMISSIONS),
        "request_id": str(uuid.uuid4())[:12],
        "latency_ms": rng.randint(900,5000),
        "concurrency": rng.randint(30,140),
        "cpu_pct": rng.randint(65,99),
        "memory_mb": rng.choice([256,512,1024]),
        "restart_count": rng.randint(3,20),
        "age_s": rng.randint(60,900),
        "unacked": rng.randint(500,25000),
        "active": rng.randint(90,180),
        "max_conn": rng.choice([100,120,150]),
    }
    return {
        "severity": s.severity,
        "service": s.service,
        "status_code": s.status_code,
        "message": rng.choice(s.templates).format(**values),
        "resource_name": values["resource"],
    }