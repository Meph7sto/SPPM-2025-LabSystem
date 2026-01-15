from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ...core.errors import AppError, ErrorCode, NotFoundError
from ...core.response import ok
from ...db.session import get_db
from ...models.device import Device, DeviceStatus
from ...models.maintenance_window import MaintenanceWindow
from ...models.reservation import Reservation, ReservationStatus
from ...models.user import User, UserRole
from ...schemas.maintenance_window import (
    MaintenanceWindowCreate,
    MaintenanceWindowDetail,
    MaintenanceWindowOut,
    MaintenanceWindowUpdate,
)
from ..deps import require_roles

router = APIRouter(prefix="/maintenance-windows")


ACTIVE_RESERVATION_STATUSES = [
    ReservationStatus.PENDING,
    ReservationStatus.ADVISOR_APPROVED,
    ReservationStatus.ADMIN_APPROVED,
    ReservationStatus.HEAD_APPROVED,
    ReservationStatus.APPROVED,
    ReservationStatus.EFFECTIVE,
    ReservationStatus.BORROWED,
]


def _validate_window(start_time: datetime, end_time: datetime) -> None:
    if start_time >= end_time:
        raise AppError(ErrorCode.INVALID_REQUEST, "检修时间窗起止时间不合法")


def _ensure_no_window_overlap(
    db: Session,
    *,
    device_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_id: int | None = None,
) -> None:
    stmt = select(func.count()).select_from(MaintenanceWindow).where(
        MaintenanceWindow.device_id == device_id,
        MaintenanceWindow.start_time < end_time,
        MaintenanceWindow.end_time > start_time,
    )
    if exclude_id is not None:
        stmt = stmt.where(MaintenanceWindow.id != exclude_id)
    if int(db.execute(stmt).scalar() or 0) > 0:
        raise AppError(ErrorCode.CONFLICT, "检修时间窗与已有记录冲突")


def _ensure_no_active_reservations(
    db: Session,
    *,
    device_id: int,
    start_time: datetime,
    end_time: datetime,
) -> None:
    stmt = select(func.count()).select_from(Reservation).where(
        Reservation.device_id == device_id,
        Reservation.status.in_(ACTIVE_RESERVATION_STATUSES),
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )
    if int(db.execute(stmt).scalar() or 0) > 0:
        raise AppError(ErrorCode.CONFLICT, "存在冲突预约记录，无法设置检修时间窗")


@router.post("", response_model=dict)
def create_maintenance_window(
    payload: MaintenanceWindowCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """创建检修时间窗（管理员/负责人）。"""
    _validate_window(payload.start_time, payload.end_time)

    device = db.get(Device, payload.device_id)
    if not device:
        raise NotFoundError(f"设备不存在 (id={payload.device_id})")
    if device.status == DeviceStatus.SCRAPPED:
        raise AppError(ErrorCode.CONFLICT, "设备已报废，无法设置检修时间窗")

    _ensure_no_window_overlap(
        db,
        device_id=payload.device_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    _ensure_no_active_reservations(
        db,
        device_id=payload.device_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )

    window = MaintenanceWindow(
        device_id=payload.device_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        reason=payload.reason,
        created_by=current_user.id,
    )
    db.add(window)
    db.commit()
    db.refresh(window)
    response = MaintenanceWindowOut.model_validate(window).model_dump()
    return ok(response, message="检修时间窗创建成功")


@router.get("", response_model=dict)
def list_maintenance_windows(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    device_id: int | None = Query(None, description="按设备筛选"),
    start_time: datetime | None = Query(None, description="筛选起始时间 (包含此时段)"),
    end_time: datetime | None = Query(None, description="筛选结束时间 (包含此时段)"),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取检修时间窗列表（管理员/负责人）。"""
    stmt = select(MaintenanceWindow).options(joinedload(MaintenanceWindow.device))
    if device_id:
        stmt = stmt.where(MaintenanceWindow.device_id == device_id)
    if start_time:
        stmt = stmt.where(MaintenanceWindow.end_time > start_time)
    if end_time:
        stmt = stmt.where(MaintenanceWindow.start_time < end_time)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    stmt = stmt.order_by(MaintenanceWindow.start_time.desc()).offset(skip).limit(limit)
    windows = db.execute(stmt).scalars().all()

    return ok({
        "items": [MaintenanceWindowDetail.model_validate(item).model_dump() for item in windows],
        "total": total,
        "skip": skip,
        "limit": limit,
    })


@router.get("/{window_id}", response_model=dict)
def get_maintenance_window(
    window_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取检修时间窗详情（管理员/负责人）。"""
    window = db.execute(
        select(MaintenanceWindow)
        .options(joinedload(MaintenanceWindow.device))
        .where(MaintenanceWindow.id == window_id)
    ).scalar_one_or_none()
    if not window:
        raise NotFoundError(f"检修时间窗不存在 (id={window_id})")
    return ok(MaintenanceWindowDetail.model_validate(window).model_dump())


@router.put("/{window_id}", response_model=dict)
def update_maintenance_window(
    window_id: int,
    payload: MaintenanceWindowUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """更新检修时间窗（管理员/负责人）。"""
    window = db.get(MaintenanceWindow, window_id)
    if not window:
        raise NotFoundError(f"检修时间窗不存在 (id={window_id})")

    update_data = payload.model_dump(exclude_unset=True)
    target_start = update_data.get("start_time", window.start_time)
    target_end = update_data.get("end_time", window.end_time)
    _validate_window(target_start, target_end)

    _ensure_no_window_overlap(
        db,
        device_id=window.device_id,
        start_time=target_start,
        end_time=target_end,
        exclude_id=window.id,
    )
    _ensure_no_active_reservations(
        db,
        device_id=window.device_id,
        start_time=target_start,
        end_time=target_end,
    )

    for key, value in update_data.items():
        setattr(window, key, value)

    db.commit()
    db.refresh(window)
    return ok(MaintenanceWindowOut.model_validate(window).model_dump(), message="检修时间窗更新成功")


@router.delete("/{window_id}", response_model=dict)
def delete_maintenance_window(
    window_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """删除检修时间窗（管理员/负责人）。"""
    window = db.get(MaintenanceWindow, window_id)
    if not window:
        raise NotFoundError(f"检修时间窗不存在 (id={window_id})")
    db.delete(window)
    db.commit()
    return ok({"id": window_id}, message="检修时间窗删除成功")
