from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..models.notification import NotificationType


class NotificationBase(BaseModel):
    title: str
    content: str
    type: NotificationType = Field(description="通知类型")
    from_user_id: int | None = None
    to_user_id: int
    meta: dict[str, Any] | None = None


class NotificationOut(NotificationBase):
    id: int
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    total: int
    skip: int
    limit: int


class MarkReadIn(BaseModel):
    ids: list[int] = Field(min_length=1, description="要标记已读的通知 ID 列表")

