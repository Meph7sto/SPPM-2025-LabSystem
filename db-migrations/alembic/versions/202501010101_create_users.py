"""create users table

Revision ID: 202501010101
Revises: 
Create Date: 2025-01-01 01:01:01

"""
from alembic import op
import sqlalchemy as sa

revision = "202501010101"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("admin", "head", "borrower", name="user_role", native_enum=False)
borrower_type = sa.Enum(
    "teacher",
    "student",
    "external",
    name="borrower_type",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("account", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("borrower_type", borrower_type, nullable=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("contact", sa.String(length=64), nullable=False),
        sa.Column("college", sa.String(length=128), nullable=True),
        sa.Column("teacher_no", sa.String(length=32), nullable=True),
        sa.Column("student_no", sa.String(length=32), nullable=True),
        sa.Column("advisor_no", sa.String(length=32), nullable=True),
        sa.Column("org_name", sa.String(length=128), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("account", name="uq_users_account"),
        sa.UniqueConstraint("teacher_no", name="uq_users_teacher_no"),
        sa.UniqueConstraint("student_no", name="uq_users_student_no"),
    )


def downgrade() -> None:
    op.drop_table("users")
