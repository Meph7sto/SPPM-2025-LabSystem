from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field

from ..models.device import DeviceStatus

class DeviceBase(BaseModel):
    """设备基础模型"""
    device_no: str = Field(..., max_length=64, description="设备编号")
    model: str | None = Field(None, max_length=128, description="型号")
    purchase_date: date | None = Field(None, description="购买日期")
    manufacturer: str | None = Field(None, max_length=128, description="生产厂家")
    usage: str | None = Field(None, description="用途说明")
    rental_price: float | None = Field(0.0, ge=0, description="租金单价")
    status: DeviceStatus = Field(DeviceStatus.IDLE, description="状态")

class DeviceCreate(DeviceBase):
    """创建设备请求"""
    pass

class DeviceUpdate(BaseModel):
    """更新设备请求"""
    device_no: str | None = Field(None, max_length=64)
    model: str | None = Field(None, max_length=128)
    purchase_date: date | None = None
    manufacturer: str | None = Field(None, max_length=128)
    usage: str | None = None
    rental_price: float | None = Field(None, ge=0)
    status: DeviceStatus | None = None

class DeviceOut(DeviceBase):
    """设备输出模型"""
    id: int

    class Config:
        from_attributes = True
