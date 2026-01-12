from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class FinancePayment(Base):
    """财务侧支付单（用于对接/Mock）。"""

    __tablename__ = "finance_payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id"), unique=True, index=True, nullable=False
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    paid_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class RefundRecord(Base):
    """退款记录（BRULE-6: 付费预约仅退 95%）。"""

    __tablename__ = "refund_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"), index=True, nullable=False)
    order_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    original_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    refund_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    refund_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="processed")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
