from __future__ import annotations

from pydantic import BaseModel


class DeviceAvailabilityItem(BaseModel):
    """
    设备可用性看板项。
    用于前端展示设备的时间轴状态。
    """
    id: int
    device_no: str
    name: str
    meta: str
    status: str
    status_class: str
    zone: str
