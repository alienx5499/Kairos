from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..infrastructure.db import get_db
import logging
from ..infrastructure.metrics import get_metrics_payload, record_incident_state
from ..infrastructure.repository_impl import SqlAlchemyIncidentRepository
from ..application.use_cases import GetIncidentStatsUseCase, GetActiveIncidentsBySeverityUseCase

logger = logging.getLogger(__name__)

health_router = APIRouter(tags=["Health & Telemetry"])


@health_router.get("/health", status_code=status.HTTP_200_OK)
def liveness_probe():
    return {"status": "healthy", "service": "kairos-backend"}


@health_router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_probe(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return Response(
            content=f'{{"status": "degraded", "error": "{str(e)}"}}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )


@health_router.get("/metrics")
def metrics_endpoint(db: Session = Depends(get_db)):
    repo = SqlAlchemyIncidentRepository(db)
    # db outage must not break the scrape, http metrics still export
    try:
        record_incident_state(
            GetIncidentStatsUseCase(repo).execute()["total"],
            GetActiveIncidentsBySeverityUseCase(repo).execute(),
        )
    except Exception:
        logger.exception("incident gauges not refreshed")
    data, content_type = get_metrics_payload()
    return Response(content=data, media_type=content_type)
