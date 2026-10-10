from typing import List, Optional, Protocol, Dict
from ..domain.entities import Incident
from ..domain.value_objects import Severity, IncidentStatus


# storage-agnostic port for the application layer
class IncidentRepositoryProtocol(Protocol):
    def get_by_id(self, incident_id: int) -> Optional[Incident]:
        ...

    def list_all(
        self,
        status: Optional[IncidentStatus] = None,
        severity: Optional[Severity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Incident]:
        ...

    def create(self, incident: Incident) -> Incident:
        ...

    def update(self, incident: Incident) -> Incident:
        ...

    def delete(self, incident_id: int) -> bool:
        ...

    def get_stats(self) -> Dict[str, int]:
        ...
