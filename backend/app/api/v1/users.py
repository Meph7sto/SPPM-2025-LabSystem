from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.errors import AppError, ErrorCode
from ...core.response import ok
from ...db.session import get_db
from ...models.user import User
from ...models.reservation import Reservation
from ...schemas.auth import UserOut
from ...schemas.user import UpdateProfileRequest
from ...schemas.reservation import ReservationDetail
from ..deps import get_current_user

router = APIRouter(prefix="/users")


def to_user_out(user: User) -> UserOut:
    return UserOut.model_validate(user)


@router.get("/me/profile", response_model=dict)
def get_my_profile(current_user: User = Depends(get_current_user)) -> dict:
    """获取当前用户的个人资料"""
    return ok(to_user_out(current_user).model_dump())


@router.put("/me/profile", response_model=dict)
def update_my_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """更新当前用户的个人资料"""
    # 只更新提供的字段
    if payload.name is not None:
        current_user.name = payload.name
    if payload.contact is not None:
        current_user.contact = payload.contact
    if payload.college is not None:
        current_user.college = payload.college
    if payload.org_name is not None:
        current_user.org_name = payload.org_name

    db.commit()
    db.refresh(current_user)

    return ok(
        to_user_out(current_user).model_dump(),
        message="Profile updated successfully",
    )


@router.get("/me/reservations", response_model=dict)
def get_my_reservations(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取当前用户的所有预约记录（我的预约入口）"""
    # 查询当前用户的所有预约
    stmt = (
        select(Reservation)
        .where(Reservation.user_id == current_user.id)
        .order_by(Reservation.start_time.desc())
        .offset(skip)
        .limit(limit)
    )
    
    reservations = db.execute(stmt).scalars().all()
    
    # 转换为详细信息输出
    result = [ReservationDetail.model_validate(r) for r in reservations]
    
    return ok(
        [r.model_dump() for r in result],
        message="My reservations retrieved successfully",
    )

