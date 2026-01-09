from __future__ import annotations

import enum
from datetime import date
from sqlalchemy import Date, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base

class DeviceStatus(str, enum.Enum):
    IDLE = "idle"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    SCRAPPED = "scrapped"

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_no: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(128))
    purchase_date: Mapped[date] = mapped_column(Date)
    manufacturer: Mapped[str] = mapped_column(String(128))
    usage: Mapped[str] = mapped_column(Text)
    rental_price: Mapped[float] = mapped_column(Float)
    status: Mapped[DeviceStatus] = mapped_column(
        Enum(DeviceStatus, name="device_status", native_enum=False),
        default=DeviceStatus.IDLE,
        nullable=False,
    )
