from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from .db import Base


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    service_name = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(30), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    responder = Column(String(100), nullable=False)
    root_cause = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # combined status + severity filter
    __table_args__ = (
        Index("ix_incidents_status_severity", "status", "severity"),
    )
