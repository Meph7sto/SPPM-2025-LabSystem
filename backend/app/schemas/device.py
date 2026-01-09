from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field

from ..models.device import DeviceStatus

class DeviceBase(BaseModel):
    device_no: str = Field(..., max_length=64, description="Unique device number")
    model: str | None = Field(None, max_length=128)
    purchase_date: date | None = None
    manufacturer: str | None = Field(None, max_length=128)
    usage: str | None = None
    rental_price: float | None = Field(0.0, ge=0)
    status: DeviceStatus = DeviceStatus.IDLE

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    device_no: str | None = Field(None, max_length=64)
    model: str | None = Field(None, max_length=128)
    purchase_date: date | None = None
    manufacturer: str | None = Field(None, max_length=128)
    usage: str | None = None
    rental_price: float | None = Field(None, ge=0)
    status: DeviceStatus | None = None

class DeviceOut(DeviceBase):
    id: int

    class Config:
        from_attributes = True
