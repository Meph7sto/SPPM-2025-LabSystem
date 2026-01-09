from __future__ import annotations

import enum
from datetime import datetime
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class ReservationStatus(str, enum.Enum):
    """预约状态枚举"""
    PENDING = "pending"              # 待审批
    ADVISOR_APPROVED = "advisor_approved"  # 导师已审批（学生申请）
    ADMIN_APPROVED = "admin_approved"      # 管理员已审批
    HEAD_APPROVED = "head_approved"        # 负责人已审批（校外申请）
    APPROVED = "approved"            # 最终审批通过
    REJECTED = "rejected"            # 已驳回
    RETURNED = "returned"            # 退回补充材料
    EFFECTIVE = "effective"          # 已生效（可借出）
    BORROWED = "borrowed"            # 已借出
    COMPLETED = "completed"          # 已完成（已归还）
    CANCELLED = "cancelled"          # 已取消


class PaymentStatus(str, enum.Enum):
    """支付状态枚举"""
    NOT_REQUIRED = "not_required"    # 无需支付（校内人员）
    PENDING = "pending"              # 待支付
    PAID = "paid"                    # 已支付
    REFUNDED = "refunded"            # 已退款
    WAIVED = "waived"                # 已免除


class ApprovalStep(str, enum.Enum):
    """审批步骤枚举"""
    ADVISOR = "advisor"              # 导师审批
    ADMIN = "admin"                  # 管理员审批
    HEAD = "head"                    # 负责人审批
    PAYMENT = "payment"              # 缴费确认
    FINAL = "final"                  # 最终确认


class Reservation(Base):
    """预约台账模型
    
    包含设备/人员/时段/审批/支付/状态字段（FR-6）
    """
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 设备信息
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False)
    
    # 人员信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # 时段信息
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # 用途说明
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # 状态信息
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, name="reservation_status", native_enum=False),
        default=ReservationStatus.PENDING,
        nullable=False,
    )
    
    # 当前审批步骤
    current_step: Mapped[ApprovalStep | None] = mapped_column(
        Enum(ApprovalStep, name="approval_step", native_enum=False),
        nullable=True,
    )
    
    # 审批信息
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approval_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 导师审批（学生申请）
    advisor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    advisor_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    advisor_approval_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 负责人审批（校外申请）
    head_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    head_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    head_approval_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 支付信息
    payment_amount: Mapped[float] = mapped_column(Float, default=0.0)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status", native_enum=False),
        default=PaymentStatus.NOT_REQUIRED,
        nullable=False,
    )
    payment_order_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payment_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refund_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    refund_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 借出/归还信息
    borrow_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    return_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    handover_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    return_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    device = relationship("Device", backref="reservations")
    user = relationship("User", foreign_keys=[user_id], backref="reservations")
    approver = relationship("User", foreign_keys=[approver_id], backref="approved_reservations")
    advisor = relationship("User", foreign_keys=[advisor_id], backref="advisor_approved_reservations")
    head = relationship("User", foreign_keys=[head_id], backref="head_approved_reservations")
