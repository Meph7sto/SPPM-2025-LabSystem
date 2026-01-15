from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class NotificationType(str, enum.Enum):
    SUBMIT_SUCCESS = "submit_success"
    APPROVAL_RESULT = "approval_result"
    PAYMENT_CONFIRMED = "payment_confirmed"
    RESERVATION_CANCELLED = "reservation_cancelled"
    REFUND_PROCESSED = "refund_processed"
    REPORT_GENERATED = "report_generated"
    OVERDUE_REMINDER = "overdue_reminder"


class Notification(Base):
    """系统提醒/站内通知表。"""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        String(50), nullable=False
    )  # 使用字符串枚举以便轻量扩展

    from_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    meta: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

