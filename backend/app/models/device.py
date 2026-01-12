from __future__ import annotations

import enum
from datetime import date
from sqlalchemy import Date, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base

class DeviceStatus(str, enum.Enum):
    """
    设备状态枚举。
    用于描述设备当前的可用性情况。
    """
    IDLE = "idle"              # 闲置/可借：设备在库，功能正常，可以被预约
    IN_USE = "in_use"          # 使用中/已借出：设备当前已被借出，不可预约
    MAINTENANCE = "maintenance" # 维修/保养中：设备正在进行维护或维修，暂停借用
    SCRAPPED = "scrapped"      # 已报废：设备已达到使用寿命或损坏无法修复，停止使用

class Device(Base):
    """
    设备台账模型。
    对应数据库表 `devices`。

    存储实验室所有设备的详细信息，包括资产编号、型号、状态等。
    该模型是资产管理核心模块的基础数据。
    """
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 设备编号（资产编号）
    # 唯一标识设备的字符串，通常贴在设备标签上
    device_no: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # 设备型号
    # 具体的规格型号字符串
    model: Mapped[str] = mapped_column(String(128))

    # 购买日期
    # 设备入库或购买的时间，用于计算折旧或维保
    purchase_date: Mapped[date] = mapped_column(Date)

    # 生产厂家
    # 设备的品牌或制造厂商名称
    manufacturer: Mapped[str] = mapped_column(String(128))

    # 用途说明
    # 描述设备的主要功能或适用实验场景
    usage: Mapped[str] = mapped_column(Text)

    # 租借费用（单价）
    # 每次或每天的租借费用，默认为 0.0
    rental_price: Mapped[float] = mapped_column(Float)

    # 设备状态
    # 记录当前设备是否可借，默认为 IDLE (闲置)
    status: Mapped[DeviceStatus] = mapped_column(
        Enum(DeviceStatus, name="device_status", native_enum=False),
        default=DeviceStatus.IDLE,
        nullable=False,
    )
