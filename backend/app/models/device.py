from __future__ import annotations

import enum
from datetime import date
from sqlalchemy import Date, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base

class DeviceStatus(str, enum.Enum):
    """设备状态枚举"""
    IDLE = "idle"              # 闲置/可借
    IN_USE = "in_use"          # 使用中/已借出
    MAINTENANCE = "maintenance" # 维修/保养中
    SCRAPPED = "scrapped"      # 已报废

class Device(Base):
    """
    设备模型。
    存储实验室设备信息。
    """
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    # 设备编号（资产编号）
    device_no: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    # 设备型号
    model: Mapped[str] = mapped_column(String(128))
    # 购买日期
    purchase_date: Mapped[date] = mapped_column(Date)
    # 生产厂家
    manufacturer: Mapped[str] = mapped_column(String(128))
    # 用途说明
    usage: Mapped[str] = mapped_column(Text)
    # 租借费用（单价）
    rental_price: Mapped[float] = mapped_column(Float)
    # 设备状态
    status: Mapped[DeviceStatus] = mapped_column(
        Enum(DeviceStatus, name="device_status", native_enum=False),
        default=DeviceStatus.IDLE,
        nullable=False,
    )
