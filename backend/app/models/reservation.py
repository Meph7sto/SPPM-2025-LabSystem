from __future__ import annotations

import enum
from datetime import datetime
from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class ReservationStatus(str, enum.Enum):
    """
    预约状态枚举。
    描述预约单在整个生命周期中的流转状态。
    """
    PENDING = "pending"              # 待审批：用户刚提交，等待进入审批流程
    ADVISOR_APPROVED = "advisor_approved"  # 导师已审批：学生提交的申请，导师已同意
    ADMIN_APPROVED = "admin_approved"      # 管理员已审批：管理员审核通过，等待后续步骤（如负责人审批）
    HEAD_APPROVED = "head_approved"        # 负责人已审批：针对校外人员申请，负责人已同意
    APPROVED = "approved"            # 最终审批通过：所有必要的审批步骤已完成，但尚未生效（可能等待支付）
    REJECTED = "rejected"            # 已驳回：审批过程中被任一审批人拒绝
    RETURNED = "returned"            # 退回补充材料：审批人认为信息不全，退回给申请人修改
    EFFECTIVE = "effective"          # 已生效（可借出）：审批通过且（如需）支付完成，等待领取设备
    BORROWED = "borrowed"            # 已借出：设备已被用户领取，正在使用中
    COMPLETED = "completed"          # 已完成：设备已归还，流程结束
    CANCELLED = "cancelled"          # 已取消：用户在流程结束前主动取消申请


class PaymentStatus(str, enum.Enum):
    """
    支付状态枚举。
    用于跟踪费用的缴纳情况。
    """
    NOT_REQUIRED = "not_required"    # 无需支付：通常适用于校内人员
    PENDING = "pending"              # 待支付：审批通过，等待用户付款
    PAID = "paid"                    # 已支付：用户已完成付款
    REFUNDED = "refunded"            # 已退款：发生退款操作
    WAIVED = "waived"                # 已免除：管理员手动免除费用


class ApprovalStep(str, enum.Enum):
    """
    审批步骤枚举。
    标记当前预约单正处于哪个审批环节。
    """
    ADVISOR = "advisor"              # 导师审批环节（仅学生）
    ADMIN = "admin"                  # 管理员审批环节
    HEAD = "head"                    # 负责人审批环节（仅校外人员）
    PAYMENT = "payment"              # 缴费确认环节
    FINAL = "final"                  # 最终确认环节（通常指审批流程结束）


class Reservation(Base):
    """
    预约台账模型。
    对应数据库表 `reservations`。
    
    记录设备借用的完整信息，包括申请人、设备、时间段、审批流记录、支付记录以及状态流转。
    该表是系统的核心业务表，关联了 User 和 Device。
    """
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # -------------------------------------------------------------------------
    # 基础信息
    # -------------------------------------------------------------------------

    # 关联设备 ID
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False)
    
    # 关联申请人 ID
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # 预约起始时间
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # 预约结束时间
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # 用途说明 (申请理由)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # 申请人联系方式 (备份，可能与用户表不同)
    contact: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # -------------------------------------------------------------------------
    # 状态与流程控制
    # -------------------------------------------------------------------------

    # 当前预约状态
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, name="reservation_status", native_enum=False),
        default=ReservationStatus.PENDING,
        nullable=False,
    )
    
    # 当前待处理的审批步骤
    current_step: Mapped[ApprovalStep | None] = mapped_column(
        Enum(ApprovalStep, name="approval_step", native_enum=False),
        nullable=True,
    )
    
    # -------------------------------------------------------------------------
    # 审批记录
    # -------------------------------------------------------------------------

    # 1. 管理员审批信息
    approver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approval_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 2. 导师审批信息（仅学生申请涉及）
    advisor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    advisor_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    advisor_approval_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 3. 负责人审批信息（仅校外申请涉及）
    head_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    head_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    head_approval_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # -------------------------------------------------------------------------
    # 支付信息
    # -------------------------------------------------------------------------

    # 应付金额
    payment_amount: Mapped[float] = mapped_column(Float, default=0.0)

    # 支付状态
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status", native_enum=False),
        default=PaymentStatus.NOT_REQUIRED,
        nullable=False,
    )

    # 支付订单号 (外部支付系统流水号)
    payment_order_no: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # 支付完成时间
    payment_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 退款金额
    refund_amount: Mapped[float | None] = mapped_column(Float, nullable=True)

    # 退款时间
    refund_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # -------------------------------------------------------------------------
    # 借还交接信息
    # -------------------------------------------------------------------------

    # 实际借出时间 (设备被取走的时间)
    borrow_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 实际归还时间 (设备还回的时间)
    return_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 交接备注 (借出时)
    handover_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 归还备注 (归还时，如设备检查情况)
    return_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # -------------------------------------------------------------------------
    # 元数据
    # -------------------------------------------------------------------------

    # 记录创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 记录更新时间
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # 关联关系 (Relationships)
    # -------------------------------------------------------------------------

    # 关联的设备对象
    device = relationship("Device", backref="reservations")

    # 关联的申请人对象
    user = relationship("User", foreign_keys=[user_id], backref="reservations")

    # 关联的管理员审批人对象
    approver = relationship("User", foreign_keys=[approver_id], backref="approved_reservations")

    # 关联的导师审批人对象
    advisor = relationship("User", foreign_keys=[advisor_id], backref="advisor_approved_reservations")

    # 关联的负责人审批人对象
    head = relationship("User", foreign_keys=[head_id], backref="head_approved_reservations")
