"""Add borrower demographic fields

Revision ID: 20260115_add_user_demographics
Revises: 20260113_add_notifications
Create Date: 2026-01-15
"""

from alembic import op
import sqlalchemy as sa


revision = "20260115_add_user_demographics"
down_revision = "20260113_add_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("gender", sa.String(length=16), nullable=True))
    op.add_column("users", sa.Column("professional_title", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("research_direction", sa.String(length=128), nullable=True))
    op.add_column("users", sa.Column("major", sa.String(length=128), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "major")
    op.drop_column("users", "research_direction")
    op.drop_column("users", "professional_title")
    op.drop_column("users", "gender")
