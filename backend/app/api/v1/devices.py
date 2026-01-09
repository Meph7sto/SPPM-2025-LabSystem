from __future__ import annotations

from datetime import date as date_cls, datetime, time as time_cls, timezone
from typing import Tuple

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ...core.errors import AppError, ErrorCode, NotFoundError
from ...core.response import ok
from ...db.session import get_db
from ...models.device import Device, DeviceStatus
from ...models.reservation import Reservation, ReservationStatus
from ...models.user import User, UserRole
from ...schemas import DeviceAvailabilityItem, DeviceCreate, DeviceOut, DeviceUpdate
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/devices")


def _parse_slot(date_str: str, slot: str) -> Tuple[datetime, datetime]:
    if not date_str:
        raise AppError(ErrorCode.INVALID_REQUEST, "date 参数不能为空")
    if not slot or "-" not in slot:
        raise AppError(ErrorCode.INVALID_REQUEST, "slot 参数格式应为 HH:MM-HH:MM")
    try:
        day = date_cls.fromisoformat(date_str)
    except ValueError as exc:
        raise AppError(ErrorCode.INVALID_REQUEST, "date 参数格式应为 YYYY-MM-DD") from exc

    start_raw, end_raw = [s.strip() for s in slot.split("-", 1)]
    try:
        start_time = time_cls.fromisoformat(start_raw)
        end_time = time_cls.fromisoformat(end_raw)
    except ValueError as exc:
        raise AppError(ErrorCode.INVALID_REQUEST, "slot 时间格式应为 HH:MM") from exc

    if start_time >= end_time:
        raise AppError(ErrorCode.INVALID_REQUEST, "slot 起止时间不合法")

    local_tz = datetime.now().astimezone().tzinfo or timezone.utc
    start_dt = datetime.combine(day, start_time, tzinfo=local_tz).astimezone(timezone.utc)
    end_dt = datetime.combine(day, end_time, tzinfo=local_tz).astimezone(timezone.utc)
    return start_dt, end_dt


def _derive_zone(device_no: str) -> str:
    prefix = (device_no or "").strip()[:1].upper()
    if prefix in {"A", "B", "C"}:
        return f"{prefix}区"
    return "未知"


def _resolve_availability_status(
    device: Device, occupied_device_ids: set[int]
) -> tuple[str, str]:
    if device.status == DeviceStatus.MAINTENANCE:
        return "检修", "chip-alert"
    if device.status == DeviceStatus.SCRAPPED:
        return "停用", "chip-neutral"
    if device.status == DeviceStatus.IN_USE or device.id in occupied_device_ids:
        return "已占用", "chip-warn"
    return "可用", "chip-good"


@router.get("/availability", response_model=dict)
def get_device_availability(
    date: str = Query(..., description="查询日期 YYYY-MM-DD"),
    slot: str = Query(..., description="时间段 HH:MM-HH:MM"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, description="搜索关键词（设备编号/型号/厂商）"),
    zone: str | None = Query(None, description="按区域筛选（A区/B区/C区）"),
    db: Session = Depends(get_db),
) -> dict:
    """获取指定日期/时段设备可用性列表"""
    start_dt, end_dt = _parse_slot(date, slot)

    stmt = select(Device)
    if keyword:
        stmt = stmt.where(
            (Device.device_no.ilike(f"%{keyword}%")) |
            (Device.model.ilike(f"%{keyword}%")) |
            (Device.manufacturer.ilike(f"%{keyword}%"))
        )

    zone_prefix = None
    if zone:
        zone_prefix = zone.strip()[:1].upper()
        if zone_prefix:
            stmt = stmt.where(Device.device_no.ilike(f"{zone_prefix}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    devices = db.execute(
        stmt.order_by(Device.id.desc()).offset(skip).limit(limit)
    ).scalars().all()

    device_ids = [d.id for d in devices]
    occupied_device_ids: set[int] = set()
    if device_ids:
        active_statuses = [
            ReservationStatus.PENDING,
            ReservationStatus.ADVISOR_APPROVED,
            ReservationStatus.ADMIN_APPROVED,
            ReservationStatus.HEAD_APPROVED,
            ReservationStatus.APPROVED,
            ReservationStatus.EFFECTIVE,
            ReservationStatus.BORROWED,
        ]
        conflict_stmt = (
            select(Reservation.device_id)
            .where(Reservation.device_id.in_(device_ids))
            .where(Reservation.status.in_(active_statuses))
            .where(Reservation.start_time < end_dt)
            .where(Reservation.end_time > start_dt)
        )
        occupied_device_ids = set(db.execute(conflict_stmt).scalars().all())

    items: list[DeviceAvailabilityItem] = []
    for device in devices:
        zone_value = _derive_zone(device.device_no)
        status, status_class = _resolve_availability_status(device, occupied_device_ids)
        meta_source = device.manufacturer or device.usage or device.model or "设备"
        items.append(DeviceAvailabilityItem(
            id=device.id,
            device_no=device.device_no,
            name=f"{device.device_no} {device.model or ''}".strip(),
            meta=f"{meta_source} | 设备编号 {device.device_no}",
            status=status,
            status_class=status_class,
            zone=zone_value,
        ))

    return ok({
        "items": [item.model_dump() for item in items],
        "total": total,
        "skip": skip,
        "limit": limit,
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
    })


@router.post("", response_model=dict)
def create_device(
    payload: DeviceCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """创建设备（管理员/负责人）
    
    设备台账 CRUD - T09 (FR-4)
    - deviceNo 唯一
    - 型号、购入时间、厂商、用途、租用价格、状态
    """
    # 检查设备编号唯一性
    stmt = select(Device).where(Device.device_no == payload.device_no)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        raise AppError(ErrorCode.INVALID_REQUEST, "设备编号已存在")

    device = Device(**payload.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return ok(DeviceOut.model_validate(device).model_dump(), message="设备创建成功")


@router.get("/{device_id}", response_model=dict)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """获取设备详情"""
    device = db.get(Device, device_id)
    if not device:
        raise NotFoundError(f"设备不存在 (id={device_id})")
    return ok(DeviceOut.model_validate(device).model_dump())


@router.get("", response_model=dict)
def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str = Query(None, description="搜索关键词（设备编号/型号/厂商）"),
    status: DeviceStatus | None = Query(None, description="按状态筛选"),
    db: Session = Depends(get_db),
) -> dict:
    """获取设备列表（支持搜索和筛选）"""
    stmt = select(Device)
    
    if keyword:
        stmt = stmt.where(
            (Device.device_no.ilike(f"%{keyword}%")) |
            (Device.model.ilike(f"%{keyword}%")) |
            (Device.manufacturer.ilike(f"%{keyword}%"))
        )
    if status:
        stmt = stmt.where(Device.status == status)
    
    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # 分页
    stmt = stmt.order_by(Device.id.desc()).offset(skip).limit(limit)
    devices = db.execute(stmt).scalars().all()
    
    return ok({
        "items": [DeviceOut.model_validate(d).model_dump() for d in devices],
        "total": total,
        "skip": skip,
        "limit": limit,
    })


@router.put("/{device_id}", response_model=dict)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """更新设备（管理员/负责人）"""
    device = db.get(Device, device_id)
    if not device:
        raise NotFoundError(f"设备不存在 (id={device_id})")
    
    update_data = payload.model_dump(exclude_unset=True)
    if "device_no" in update_data:
        # 检查设备编号唯一性
        stmt = select(Device).where(Device.device_no == update_data["device_no"])
        existing = db.execute(stmt).scalar_one_or_none()
        if existing and existing.id != device_id:
            raise AppError(ErrorCode.INVALID_REQUEST, "设备编号已存在")

    for key, value in update_data.items():
        setattr(device, key, value)
    
    db.commit()
    db.refresh(device)
    return ok(DeviceOut.model_validate(device).model_dump(), message="设备更新成功")


@router.delete("/{device_id}", response_model=dict)
def delete_device(
    device_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """删除设备（管理员/负责人）"""
    device = db.get(Device, device_id)
    if not device:
        raise NotFoundError(f"设备不存在 (id={device_id})")
    
    db.delete(device)
    db.commit()
    return ok({"id": device_id}, message="设备删除成功")


# ==================== 台账统计接口 ====================

@router.get("/ledger/stats", response_model=dict)
def get_device_ledger_stats(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取设备台账统计（管理员/负责人）"""
    # 按状态统计
    status_counts = {}
    for status in DeviceStatus:
        count = db.execute(
            select(func.count()).where(Device.status == status)
        ).scalar() or 0
        status_counts[status.value] = count
    
    total = db.execute(select(func.count()).select_from(Device)).scalar() or 0
    
    # 计算总租用价格
    total_rental = db.execute(
        select(func.sum(Device.rental_price))
    ).scalar() or 0.0
    
    return ok({
        "total": total,
        "by_status": status_counts,
        "total_rental_value": total_rental,
    })
