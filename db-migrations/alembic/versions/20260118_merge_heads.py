"""Merge heads after system config branch

Revision ID: 20260118_merge_heads
Revises: 20260117_add_reservation_overdue_notified_at, 430c8a0d2252
Create Date: 2026-01-18
"""

from alembic import op


revision = "20260118_merge_heads"
down_revision = ("20260117_add_reservation_overdue_notified_at", "430c8a0d2252")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
