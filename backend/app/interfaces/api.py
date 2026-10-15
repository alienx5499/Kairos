from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from ..infrastructure.db import get_db
from ..infrastructure.repository_impl import SqlAlchemyIncidentRepository
from ..application.use_cases import (
    CreateIncidentUseCase,
    UpdateIncidentUseCase,
    GetIncidentUseCase,
    ListIncidentsUseCase,
    DeleteIncidentUseCase,
    GetIncidentStatsUseCase
)
from ..domain.value_objects import Severity, IncidentStatus
from .schemas import IncidentCreate, IncidentUpdate, IncidentResponse, IncidentStatsResponse

router = APIRouter(prefix="/api/v1/incidents", tags=["Incidents"])


def get_repository(db: Session = Depends(get_db)) -> SqlAlchemyIncidentRepository:
    return SqlAlchemyIncidentRepository(db)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    repo: SqlAlchemyIncidentRepository = Depends(get_repository)
):
    use_case = CreateIncidentUseCase(repo)
    incident = use_case.execute(
        title=payload.title,
        service_name=payload.service_name,
        severity=payload.severity,
        summary=payload.summary,
        responder=payload.responder
    )
    return incident


@router.get("", response_model=List[IncidentResponse])
def list_incidents(
    status: Optional[IncidentStatus] = Query(None, description="Filter by status"),
    severity: Optional[Severity] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    repo: SqlAlchemyIncidentRepository = Depends(get_repository)
):
    use_case = ListIncidentsUseCase(repo)
    return use_case.execute(status=status, severity=severity, limit=limit, offset=offset)


@router.get("/stats/summary", response_model=IncidentStatsResponse)
def get_incident_stats(
    repo: SqlAlchemyIncidentRepository = Depends(get_repository)
):
    use_case = GetIncidentStatsUseCase(repo)
    return use_case.execute()


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: int,
    repo: SqlAlchemyIncidentRepository = Depends(get_repository)
):
    use_case = GetIncidentUseCase(repo)
    incident = use_case.execute(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found"
        )
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    repo: SqlAlchemyIncidentRepository = Depends(get_repository)
):
    use_case = UpdateIncidentUseCase(repo)
    incident = use_case.execute(
        incident_id=incident_id,
        status=payload.status,
        severity=payload.severity,
        root_cause=payload.root_cause,
        responder=payload.responder
    )
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found"
        )
    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: int,
    repo: SqlAlchemyIncidentRepository = Depends(get_repository)
):
    use_case = DeleteIncidentUseCase(repo)
    deleted = use_case.execute(incident_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {incident_id} not found"
        )
    return None
