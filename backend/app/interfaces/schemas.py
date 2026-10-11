from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from ..domain.value_objects import Severity, IncidentStatus


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, json_schema_extra={"example": "Kubernetes Ingress 502 Bad Gateway"})
    service_name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "api-gateway"})
    severity: Severity = Field(default=Severity.P2_HIGH)
    summary: str = Field(..., min_length=5, json_schema_extra={"example": "Upstream pods fail health checks after deployment roll"})
    responder: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Prabal Patra"})


class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    severity: Optional[Severity] = None
    root_cause: Optional[str] = None
    responder: Optional[str] = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    service_name: str
    severity: Severity
    status: IncidentStatus
    summary: str
    responder: str
    root_cause: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class IncidentStatsResponse(BaseModel):
    total: int
    investigating: int
    mitigated: int
    resolved: int
    p1_active: int
