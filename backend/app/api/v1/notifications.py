from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..deps import get_current_user, get_db
from ...models.notification import Notification
from ...models.user import User
from ...schemas.notification import (
    MarkReadIn,
    NotificationListOut,
    NotificationOut,
)
from ...services.notifications import (
    mark_all_read,
    mark_read,
)
from ...core.response import ok

router = APIRouter(prefix="/notifications")


@router.get("", response_model=dict)
def list_notifications(
    is_read: bool | None = Query(None, description="按已读状态过滤"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    filters = [Notification.to_user_id == current_user.id]
    if is_read is not None:
        filters.append(Notification.is_read.is_(is_read))

    # 主查询
    items = (
        db.execute(
            select(Notification)
            .where(*filters)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        .scalars()
        .all()
    )

    total_stmt = select(func.count()).select_from(Notification).where(*filters)
    total = db.scalar(total_stmt) or 0

    return ok(
        NotificationListOut(
            items=[NotificationOut.model_validate(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
        ).model_dump()
    )


@router.post("/mark-read", response_model=dict)
def mark_notifications_read(
    payload: MarkReadIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    affected = mark_read(db, user_id=current_user.id, ids=payload.ids)
    db.commit()
    return ok({"updated": affected}, message="已标记为已读")


@router.post("/mark-all-read", response_model=dict)
def mark_notifications_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    affected = mark_all_read(db, user_id=current_user.id)
    db.commit()
    return ok({"updated": affected}, message="已全部已读")
