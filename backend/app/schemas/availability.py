from __future__ import annotations

from pydantic import BaseModel


class DeviceAvailabilityItem(BaseModel):
    """
    设备可用性看板项模型。

    用于前端“设备状态看板”或“甘特图”展示。
    包含设备的标识、展示名称、元数据以及当前时间段的状态和样式类。
    """
    id: int
    device_no: str # 设备编号
    name: str      # 展示名称 (如: 编号 + 型号)
    meta: str      # 元数据描述 (如: 厂商 | 编号)

    # 状态文本 (如: 可用, 已占用, 维修)
    status: str

    # 前端样式类名 (如: chip-good, chip-warn, chip-alert)
    # 用于控制前端显示的颜色
    status_class: str

    # 区域标识 (如: A区, B区)
    zone: str
