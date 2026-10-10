"""0001_initial_incidents

Revision ID: 0001
Revises: 
Create Date: 2026-10-09 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('responder', sa.String(length=100), nullable=False),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_incidents_id', 'incidents', ['id'], unique=False)
    op.create_index('ix_incidents_status', 'incidents', ['status'], unique=False)
    op.create_index('ix_incidents_severity', 'incidents', ['severity'], unique=False)
    op.create_index('ix_incidents_service_name', 'incidents', ['service_name'], unique=False)
    op.create_index('ix_incidents_created_at', 'incidents', ['created_at'], unique=False)
    op.create_index('ix_incidents_status_severity', 'incidents', ['status', 'severity'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_incidents_status_severity', table_name='incidents')
    op.drop_index('ix_incidents_created_at', table_name='incidents')
    op.drop_index('ix_incidents_service_name', table_name='incidents')
    op.drop_index('ix_incidents_severity', table_name='incidents')
    op.drop_index('ix_incidents_status', table_name='incidents')
    op.drop_index('ix_incidents_id', table_name='incidents')
    op.drop_table('incidents')
