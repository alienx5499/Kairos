from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from .value_objects import Severity, IncidentStatus


# pure python, no orm coupling
@dataclass
class Incident:
    id: Optional[int]
    title: str
    service_name: str
    severity: Severity
    status: IncidentStatus
    summary: str
    responder: str
    root_cause: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

    def update_status(self, new_status: IncidentStatus, root_cause: Optional[str] = None) -> None:
        # reopening clears resolved_at
        if new_status == IncidentStatus.RESOLVED and not self.resolved_at:
            self.resolved_at = datetime.now(timezone.utc)
        elif new_status != IncidentStatus.RESOLVED:
            self.resolved_at = None

        if root_cause:
            self.root_cause = root_cause

        self.status = new_status
