from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HEAD = "head"
    BORROWER = "borrower"


class BorrowerType(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"
    EXTERNAL = "external"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    account: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.BORROWER,
        nullable=False,
    )
    borrower_type: Mapped[BorrowerType | None] = mapped_column(
        Enum(BorrowerType, name="borrower_type", native_enum=False),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(64))
    contact: Mapped[str] = mapped_column(String(64))
    college: Mapped[str | None] = mapped_column(String(128), nullable=True)
    teacher_no: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    student_no: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    advisor_no: Mapped[str | None] = mapped_column(String(32), nullable=True)
    org_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
