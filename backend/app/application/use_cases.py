from typing import List, Optional, Dict
from ..domain.entities import Incident
from ..domain.value_objects import Severity, IncidentStatus
from .repositories import IncidentRepositoryProtocol


class CreateIncidentUseCase:
    def __init__(self, repo: IncidentRepositoryProtocol):
        self.repo = repo

    def execute(
        self,
        title: str,
        service_name: str,
        severity: Severity,
        summary: str,
        responder: str
    ) -> Incident:
        # new incidents always start investigating
        incident = Incident(
            id=None,
            title=title.strip(),
            service_name=service_name.strip().lower(),
            severity=severity,
            status=IncidentStatus.INVESTIGATING,
            summary=summary.strip(),
            responder=responder.strip()
        )
        return self.repo.create(incident)


class UpdateIncidentUseCase:
    def __init__(self, repo: IncidentRepositoryProtocol):
        self.repo = repo

    def execute(
        self,
        incident_id: int,
        status: Optional[IncidentStatus] = None,
        severity: Optional[Severity] = None,
        root_cause: Optional[str] = None,
        responder: Optional[str] = None
    ) -> Optional[Incident]:
        # resolved_at rules live in the domain
        incident = self.repo.get_by_id(incident_id)
        if not incident:
            return None

        if status:
            incident.update_status(status, root_cause)
        if severity:
            incident.severity = severity
        if responder:
            incident.responder = responder.strip()

        return self.repo.update(incident)


class GetIncidentUseCase:
    def __init__(self, repo: IncidentRepositoryProtocol):
        self.repo = repo

    def execute(self, incident_id: int) -> Optional[Incident]:
        return self.repo.get_by_id(incident_id)


class ListIncidentsUseCase:
    def __init__(self, repo: IncidentRepositoryProtocol):
        self.repo = repo

    def execute(
        self,
        status: Optional[IncidentStatus] = None,
        severity: Optional[Severity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Incident]:
        return self.repo.list_all(status=status, severity=severity, limit=limit, offset=offset)


class DeleteIncidentUseCase:
    def __init__(self, repo: IncidentRepositoryProtocol):
        self.repo = repo

    def execute(self, incident_id: int) -> bool:
        return self.repo.delete(incident_id)


class GetIncidentStatsUseCase:
    def __init__(self, repo: IncidentRepositoryProtocol):
        self.repo = repo

    def execute(self) -> Dict[str, int]:
        return self.repo.get_stats()
