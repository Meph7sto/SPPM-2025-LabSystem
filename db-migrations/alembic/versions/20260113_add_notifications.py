"""Add notifications table for system reminders

Revision ID: 20260113_add_notifications
Revises: 20260112_finance_integration
Create Date: 2026-01-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260113_add_notifications"
down_revision = "20260112_finance_integration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("from_user_id", sa.Integer(), nullable=True),
        sa.Column("to_user_id", sa.Integer(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["from_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["to_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_to_user_created"), "notifications", ["to_user_id", "created_at"])
    op.create_index(op.f("ix_notifications_to_user_unread"), "notifications", ["to_user_id", "is_read", "created_at"])


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_to_user_unread"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_to_user_created"), table_name="notifications")
    op.drop_table("notifications")
