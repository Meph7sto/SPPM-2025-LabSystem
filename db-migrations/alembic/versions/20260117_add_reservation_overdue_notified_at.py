"""Add reservation overdue notified timestamp

Revision ID: 20260117_add_reservation_overdue_notified_at
Revises: 20260116_add_maintenance_windows
Create Date: 2026-01-17
"""

from alembic import op
import sqlalchemy as sa


revision = "20260117_add_reservation_overdue_notified_at"
down_revision = "20260116_add_maintenance_windows"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("reservations") as batch_op:
        batch_op.add_column(sa.Column("overdue_notified_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("reservations") as batch_op:
        batch_op.drop_column("overdue_notified_at")
