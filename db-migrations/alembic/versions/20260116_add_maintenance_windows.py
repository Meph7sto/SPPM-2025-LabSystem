"""Add maintenance windows

Revision ID: 20260116_add_maintenance_windows
Revises: 20260115_add_user_demographics
Create Date: 2026-01-16
"""

from alembic import op
import sqlalchemy as sa


revision = "20260116_add_maintenance_windows"
down_revision = "20260115_add_user_demographics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "maintenance_windows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_maintenance_windows_device_time"),
        "maintenance_windows",
        ["device_id", "start_time", "end_time"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_maintenance_windows_device_time"), table_name="maintenance_windows")
    op.drop_table("maintenance_windows")
