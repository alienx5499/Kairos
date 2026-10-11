from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..infrastructure.db import get_db
from ..infrastructure.metrics import get_metrics_payload

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
def metrics_endpoint():
    data, content_type = get_metrics_payload()
    return Response(content=data, media_type=content_type)
