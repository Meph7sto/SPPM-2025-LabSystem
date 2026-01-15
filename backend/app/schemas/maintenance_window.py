from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .device import DeviceOut


class MaintenanceWindowBase(BaseModel):
    device_id: int = Field(..., description="设备 ID")
    start_time: datetime = Field(..., description="检修开始时间")
    end_time: datetime = Field(..., description="检修结束时间")
    reason: str | None = Field(None, max_length=255, description="检修原因/说明")


class MaintenanceWindowCreate(MaintenanceWindowBase):
    pass


class MaintenanceWindowUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    reason: str | None = None


class MaintenanceWindowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    start_time: datetime
    end_time: datetime
    reason: str | None
    created_by: int | None
    created_at: datetime
    updated_at: datetime


class MaintenanceWindowDetail(MaintenanceWindowOut):
    device: DeviceOut
