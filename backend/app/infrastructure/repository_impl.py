from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..domain.entities import Incident
from ..domain.value_objects import Severity, IncidentStatus
from ..application.repositories import IncidentRepositoryProtocol
from .models import IncidentModel


class SqlAlchemyIncidentRepository(IncidentRepositoryProtocol):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: IncidentModel) -> Incident:
        return Incident(
            id=model.id,
            title=model.title,
            service_name=model.service_name,
            severity=Severity(model.severity),
            status=IncidentStatus(model.status),
            summary=model.summary,
            responder=model.responder,
            root_cause=model.root_cause,
            created_at=model.created_at,
            resolved_at=model.resolved_at
        )

    def get_by_id(self, incident_id: int) -> Optional[Incident]:
        model = self.db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
        return self._to_entity(model) if model else None

    def list_all(
        self,
        status: Optional[IncidentStatus] = None,
        severity: Optional[Severity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Incident]:
        query = self.db.query(IncidentModel)
        if status:
            query = query.filter(IncidentModel.status == status.value)
        if severity:
            query = query.filter(IncidentModel.severity == severity.value)

        models = query.order_by(IncidentModel.created_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def create(self, incident: Incident) -> Incident:
        model = IncidentModel(
            title=incident.title,
            service_name=incident.service_name,
            severity=incident.severity.value,
            status=incident.status.value,
            summary=incident.summary,
            responder=incident.responder,
            root_cause=incident.root_cause,
            created_at=incident.created_at,
            resolved_at=incident.resolved_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, incident: Incident) -> Incident:
        model = self.db.query(IncidentModel).filter(IncidentModel.id == incident.id).first()
        if not model:
            raise ValueError(f"Incident with ID {incident.id} not found")

        model.title = incident.title
        model.service_name = incident.service_name
        model.severity = incident.severity.value
        model.status = incident.status.value
        model.summary = incident.summary
        model.responder = incident.responder
        model.root_cause = incident.root_cause
        model.resolved_at = incident.resolved_at

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, incident_id: int) -> bool:
        model = self.db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    def get_stats(self) -> Dict[str, int]:
        from sqlalchemy import case

        # all counts in one query
        row = self.db.query(
            func.count(IncidentModel.id).label("total"),
            func.coalesce(func.sum(case((IncidentModel.status == IncidentStatus.INVESTIGATING.value, 1), else_=0)), 0).label("investigating"),
            func.coalesce(func.sum(case((IncidentModel.status == IncidentStatus.MITIGATED.value, 1), else_=0)), 0).label("mitigated"),
            func.coalesce(func.sum(case((IncidentModel.status == IncidentStatus.RESOLVED.value, 1), else_=0)), 0).label("resolved"),
            func.coalesce(func.sum(case((
                (IncidentModel.severity == Severity.P1_CRITICAL.value) & (IncidentModel.status != IncidentStatus.RESOLVED.value), 1
            ), else_=0)), 0).label("p1_active")
        ).first()

        if not row:
            return {
                "total": 0,
                "investigating": 0,
                "mitigated": 0,
                "resolved": 0,
                "p1_active": 0
            }

        return {
            "total": int(row.total or 0),
            "investigating": int(row.investigating or 0),
            "mitigated": int(row.mitigated or 0),
            "resolved": int(row.resolved or 0),
            "p1_active": int(row.p1_active or 0)
        }
