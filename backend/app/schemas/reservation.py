from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from ..models.reservation import ReservationStatus, PaymentStatus, ApprovalStep
from .auth import UserOut
from .device import DeviceOut


class ReservationBase(BaseModel):
    """预约基础字段"""
    device_id: int
    start_time: datetime
    end_time: datetime
    description: str | None = Field(None, max_length=255)


class ReservationCreate(ReservationBase):
    """预约创建请求"""
    pass


class ReservationUpdate(BaseModel):
    """预约更新请求"""
    start_time: datetime | None = None
    end_time: datetime | None = None
    description: str | None = None
    status: ReservationStatus | None = None
    current_step: ApprovalStep | None = None
    payment_status: PaymentStatus | None = None
    payment_amount: float | None = None
    approver_id: int | None = None
    approval_comment: str | None = None


class ApprovalAction(BaseModel):
    """审批操作请求"""
    action: str = Field(..., description="审批动作: approve/reject/return")
    comment: str | None = Field(None, max_length=500, description="审批意见")


class ReservationOut(BaseModel):
    """预约输出"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    device_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    description: str | None
    
    # 状态
    status: ReservationStatus
    current_step: ApprovalStep | None
    
    # 审批信息
    approver_id: int | None
    approval_comment: str | None
    approval_time: datetime | None
    advisor_id: int | None
    advisor_comment: str | None
    advisor_approval_time: datetime | None
    head_id: int | None
    head_comment: str | None
    head_approval_time: datetime | None
    
    # 支付信息
    payment_amount: float
    payment_status: PaymentStatus
    payment_order_no: str | None
    payment_time: datetime | None
    refund_amount: float | None
    refund_time: datetime | None
    
    # 借还信息
    borrow_time: datetime | None
    return_time: datetime | None
    handover_note: str | None
    return_note: str | None
    
    # 时间戳
    created_at: datetime
    updated_at: datetime


class ReservationDetail(ReservationOut):
    """预约详情（含关联对象）"""
    user: UserOut
    device: DeviceOut
    approver: UserOut | None = None
    advisor: UserOut | None = None
    head: UserOut | None = None


class ReservationListItem(BaseModel):
    """预约列表项（精简版）"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    device_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    status: ReservationStatus
    payment_status: PaymentStatus
    created_at: datetime
