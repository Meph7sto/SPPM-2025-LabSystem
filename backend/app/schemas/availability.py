from __future__ import annotations

from pydantic import BaseModel


class DeviceAvailabilityItem(BaseModel):
    id: int
    device_no: str
    name: str
    meta: str
    status: str
    status_class: str
    zone: str
