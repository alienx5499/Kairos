import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.infrastructure.db import Base, get_db
from app.domain.entities import Incident
from app.domain.value_objects import Severity, IncidentStatus

# static pool shares one in-memory db across tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_domain_entity_invariants():
    incident = Incident(
        id=None,
        title="Payment gateway timeout",
        service_name="payment-service",
        severity=Severity.P1_CRITICAL,
        status=IncidentStatus.INVESTIGATING,
        summary="High latency on Stripe webhook",
        responder="alice"
    )
    assert incident.resolved_at is None
    assert incident.status == IncidentStatus.INVESTIGATING

    incident.update_status(IncidentStatus.IDENTIFIED, root_cause="Downstream timeout")
    assert incident.status == IncidentStatus.IDENTIFIED
    assert incident.root_cause == "Downstream timeout"
    assert incident.resolved_at is None

    incident.update_status(IncidentStatus.RESOLVED)
    assert incident.status == IncidentStatus.RESOLVED
    assert incident.resolved_at is not None

    incident.update_status(IncidentStatus.INVESTIGATING)
    assert incident.status == IncidentStatus.INVESTIGATING
    assert incident.resolved_at is None


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "kairos_http_requests_total" in response.text


def test_create_incident(client):
    payload = {
        "title": "Auth token cache desync",
        "service_name": "auth-service",
        "severity": "P1_CRITICAL",
        "summary": "Redis cluster node failover caused intermittent 401s",
        "responder": "bob"
    }
    response = client.post("/api/v1/incidents", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["service_name"] == payload["service_name"]
    assert data["severity"] == "P1_CRITICAL"
    assert data["status"] == "INVESTIGATING"
    assert data["resolved_at"] is None


def test_create_incident_invalid_severity(client):
    payload = {
        "title": "Invalid Incident",
        "service_name": "billing",
        "severity": "INVALID_SEVERITY",
        "summary": "Should fail validation",
        "responder": "charlie"
    }
    response = client.post("/api/v1/incidents", json=payload)
    assert response.status_code == 422


def test_get_incident_by_id(client):
    create_res = client.post("/api/v1/incidents", json={
        "title": "Database connection pool exhaustion",
        "service_name": "order-service",
        "severity": "P2_HIGH",
        "summary": "Max connections reached on Postgres pool",
        "responder": "david"
    })
    incident_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == incident_id
    assert get_res.json()["title"] == "Database connection pool exhaustion"


def test_get_incident_not_found(client):
    response = client.get("/api/v1/incidents/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_incidents_with_filtering(client):
    client.post("/api/v1/incidents", json={
        "title": "Critical network partition",
        "service_name": "ingress",
        "severity": "P1_CRITICAL",
        "summary": "BGP route flap",
        "responder": "erin"
    })
    client.post("/api/v1/incidents", json={
        "title": "Minor log disk warning",
        "service_name": "logging",
        "severity": "P4_LOW",
        "summary": "Log partition at 80% usage",
        "responder": "frank"
    })

    res = client.get("/api/v1/incidents")
    assert res.status_code == 200
    assert len(res.json()) == 2

    res_crit = client.get("/api/v1/incidents?severity=P1_CRITICAL")
    assert res_crit.status_code == 200
    assert len(res_crit.json()) == 1
    assert res_crit.json()[0]["severity"] == "P1_CRITICAL"

    res_stat = client.get("/api/v1/incidents?status=INVESTIGATING")
    assert res_stat.status_code == 200
    assert len(res_stat.json()) == 2


def test_update_incident_and_resolution(client):
    create_res = client.post("/api/v1/incidents", json={
        "title": "Search index lag",
        "service_name": "search-service",
        "severity": "P3_MEDIUM",
        "summary": "Elasticsearch replication queue backed up",
        "responder": "grace"
    })
    incident_id = create_res.json()["id"]

    update_res = client.put(f"/api/v1/incidents/{incident_id}", json={
        "status": "RESOLVED",
        "root_cause": "Increased heap allocation and cleared stuck task"
    })
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["status"] == "RESOLVED"
    assert data["root_cause"] == "Increased heap allocation and cleared stuck task"
    assert data["resolved_at"] is not None


def test_delete_incident(client):
    create_res = client.post("/api/v1/incidents", json={
        "title": "Transient test incident",
        "service_name": "temp-service",
        "severity": "P4_LOW",
        "summary": "To be deleted",
        "responder": "heidi"
    })
    incident_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/incidents/{incident_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/incidents/{incident_id}")
    assert get_res.status_code == 404


def test_stats_summary(client):
    client.post("/api/v1/incidents", json={
        "title": "Incident A",
        "service_name": "svc-a",
        "severity": "P1_CRITICAL",
        "summary": "Issue A",
        "responder": "ivan"
    })
    inc_b = client.post("/api/v1/incidents", json={
        "title": "Incident B",
        "service_name": "svc-b",
        "severity": "P2_HIGH",
        "summary": "Issue B",
        "responder": "judy"
    }).json()

    client.put(f"/api/v1/incidents/{inc_b['id']}", json={
        "status": "RESOLVED",
        "root_cause": "Fixed config typo"
    })

    stats_res = client.get("/api/v1/incidents/stats/summary")
    assert stats_res.status_code == 200
    data = stats_res.json()
    assert data["total"] == 2
    assert data["investigating"] == 1
    assert data["resolved"] == 1
    assert data["p1_active"] == 1
