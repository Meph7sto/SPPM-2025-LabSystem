from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field

from ..models.device import DeviceStatus

class DeviceBase(BaseModel):
    """
    设备基础属性模型。
    包含创建和更新设备时共用的字段。
    """
    device_no: str = Field(..., max_length=64, description="设备编号（资产号），唯一标识")
    model: str | None = Field(None, max_length=128, description="设备型号")
    purchase_date: date | None = Field(None, description="购买/入库日期")
    manufacturer: str | None = Field(None, max_length=128, description="生产厂家")
    usage: str | None = Field(None, description="用途说明/功能描述")
    rental_price: float | None = Field(0.0, ge=0, description="租金单价（元/次或元/天）")
    status: DeviceStatus = Field(DeviceStatus.IDLE, description="设备当前状态")

class DeviceCreate(DeviceBase):
    """
    创建设备请求模型。
    继承基础属性，所有必填项与 Base 一致。
    """
    pass

class DeviceUpdate(BaseModel):
    """
    更新设备请求模型。
    所有字段均为可选，仅更新提供的字段。
    """
    device_no: str | None = Field(None, max_length=64, description="新的设备编号")
    model: str | None = Field(None, max_length=128, description="新的设备型号")
    purchase_date: date | None = Field(None, description="新的购买日期")
    manufacturer: str | None = Field(None, max_length=128, description="新的生产厂家")
    usage: str | None = Field(None, description="新的用途说明")
    rental_price: float | None = Field(None, ge=0, description="新的租金单价")
    status: DeviceStatus | None = Field(None, description="新的设备状态")

class DeviceOut(DeviceBase):
    """
    设备信息响应模型。
    在基础属性上增加数据库 ID。
    """
    id: int

    class Config:
        from_attributes = True
