import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .config import APP_NAME
from .infrastructure.db import engine, Base
from .infrastructure.models import IncidentModel
from .infrastructure.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION_SECONDS
from .interfaces.api import router as incident_router
from .interfaces.health import health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # best effort, alembic owns the schema
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    yield


app = FastAPI(
    title=APP_NAME,
    description="SRE Incident Management & Automated Outage Response Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path
    # collapse ids to bound label cardinality
    if endpoint.startswith("/api/v1/incidents/"):
        endpoint = "/api/v1/incidents/{id}"

    HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, endpoint=endpoint).observe(duration)
    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=endpoint,
        status_code=str(response.status_code)
    ).inc()

    return response


app.include_router(health_router)
app.include_router(incident_router)


@app.get("/")
def root():
    return {
        "service": APP_NAME,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }
