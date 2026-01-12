from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from ..models.reservation import ReservationStatus, PaymentStatus, ApprovalStep
from .auth import UserOut
from .device import DeviceOut


class ReservationBase(BaseModel):
    """
    预约基础属性模型。
    包含创建预约时的核心业务字段。
    """
    device_id: int = Field(..., description="预约的设备 ID")
    start_time: datetime = Field(..., description="预约开始时间")
    end_time: datetime = Field(..., description="预约结束时间")
    description: str | None = Field(None, max_length=255, description="申请理由/用途说明")
    contact: str | None = Field(None, max_length=100, description="联系方式（可覆盖默认联系方式）")


class ReservationCreate(ReservationBase):
    """
    创建预约请求模型。
    """
    pass


class ReservationUpdate(BaseModel):
    """
    更新预约请求模型。
    用于修改预约时间、状态、审批意见等。
    """
    start_time: datetime | None = None
    end_time: datetime | None = None
    description: str | None = None
    contact: str | None = None

    # 状态流转相关字段 (通常由管理员或审批逻辑修改)
    status: ReservationStatus | None = None
    current_step: ApprovalStep | None = None

    # 支付相关字段
    payment_status: PaymentStatus | None = None
    payment_amount: float | None = None

    # 审批信息
    approver_id: int | None = None
    approval_comment: str | None = None


class ApprovalAction(BaseModel):
    """
    审批操作请求模型。
    用于前端提交审批结果（通过/拒绝/退回）。
    """
    action: str = Field(..., description="审批动作: approve (通过), reject (拒绝), return (退回)")
    comment: str | None = Field(None, max_length=500, description="审批意见/备注")


class NextAction(BaseModel):
    """
    下一步审批动作提示模型。
    后端计算并返回给前端，告知当前状态审批通过后会流转到哪个状态。
    """
    status: ReservationStatus = Field(..., description="审批通过后的新状态")
    current_step: ApprovalStep | None = Field(None, description="审批通过后的新审批步骤")


class ReservationOut(BaseModel):
    """
    预约信息响应模型。
    包含预约的所有详细信息，但不包含关联对象的详细嵌套（ID 引用除外）。
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    device_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    description: str | None
    contact: str | None
    
    # 状态信息
    status: ReservationStatus
    current_step: ApprovalStep | None
    
    # 审批流记录
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
    """
    预约详情响应模型。
    在 ReservationOut 基础上，嵌套了关联对象（用户、设备、审批人）的详细信息。
    用于前端详情页展示。
    """
    user: UserOut = Field(..., description="申请人详情")
    device: DeviceOut = Field(..., description="设备详情")
    approver: UserOut | None = Field(None, description="管理员审批人详情")
    advisor: UserOut | None = Field(None, description="导师审批人详情")
    head: UserOut | None = Field(None, description="负责人审批人详情")


class ReservationListItem(BaseModel):
    """
    预约列表项响应模型。
    精简版模型，用于列表展示，减少数据传输量。
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    device_id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    status: ReservationStatus
    payment_status: PaymentStatus
    current_step: ApprovalStep | None
    description: str | None
    contact: str | None
    created_at: datetime
    
    # 嵌套核心关联对象
    device: DeviceOut
    user: UserOut

    # 计算字段
    next_action: NextAction | None = Field(None, description="下一步流转提示")
