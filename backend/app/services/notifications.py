from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..core.response import ok
from ..models.notification import Notification, NotificationType


def create_notification(
    db: Session,
    *,
    to_user_id: int,
    title: str,
    content: str,
    type: NotificationType,
    from_user_id: int | None = None,
    meta: dict[str, Any] | None = None,
) -> Notification:
    """
    创建一条通知，不提交事务，由调用方控制提交。
    """
    notification = Notification(
        to_user_id=to_user_id,
        from_user_id=from_user_id,
        title=title,
        content=content,
        type=type.value,
        meta=meta,
    )
    db.add(notification)
    return notification


def mark_read(
    db: Session,
    *,
    user_id: int,
    ids: Iterable[int],
) -> int:
    """将指定通知标记为已读，返回受影响行数。"""
    now = datetime.now(timezone.utc)
    result = db.execute(
        update(Notification)
        .where(
            Notification.id.in_(list(ids)),
            Notification.to_user_id == user_id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True, read_at=now)
    )
    return result.rowcount or 0


def mark_all_read(db: Session, *, user_id: int) -> int:
    """将当前用户所有未读标记为已读，返回受影响行数。"""
    now = datetime.now(timezone.utc)
    result = db.execute(
        update(Notification)
        .where(Notification.to_user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True, read_at=now)
    )
    return result.rowcount or 0


# 业务便捷方法
def notify_submit_success(db: Session, *, user_id: int, reservation_id: int) -> None:
    create_notification(
        db,
        to_user_id=user_id,
        type=NotificationType.SUBMIT_SUCCESS,
        title="预约提交成功",
        content=f"预约单 {reservation_id} 已提交，等待审批。",
        from_user_id=user_id,
        meta={"reservation_id": reservation_id},
    )


def notify_approval_result(
    db: Session,
    *,
    to_user_id: int,
    reservation_id: int,
    status: str,
    from_user_id: int | None,
) -> None:
    status_map = {
        "approved": "审批通过",
        "rejected": "审批已驳回",
        "returned": "补充材料后可重新提交",
    }
    content = status_map.get(status, "审批结果已更新")
    create_notification(
        db,
        to_user_id=to_user_id,
        type=NotificationType.APPROVAL_RESULT,
        title="审批结果通知",
        content=f"预约单 {reservation_id}: {content}",
        from_user_id=from_user_id,
        meta={"reservation_id": reservation_id, "status": status},
    )


def notify_payment_confirmed(
    db: Session,
    *,
    to_user_id: int,
    reservation_id: int,
    order_no: str | None,
) -> None:
    create_notification(
        db,
        to_user_id=to_user_id,
        type=NotificationType.PAYMENT_CONFIRMED,
        title="缴费确认完成",
        content="财务已确认缴费，预约进入最终确认步骤。",
        from_user_id=None,
        meta={"reservation_id": reservation_id, "order_no": order_no},
    )


def notify_reservation_cancelled(
    db: Session,
    *,
    to_user_id: int,
    reservation_id: int,
    from_user_id: int | None,
) -> None:
    create_notification(
        db,
        to_user_id=to_user_id,
        type=NotificationType.RESERVATION_CANCELLED,
        title="预约已撤销",
        content=f"预约单 {reservation_id} 已撤销。",
        from_user_id=from_user_id,
        meta={"reservation_id": reservation_id},
    )


def notify_refund_processed(
    db: Session,
    *,
    to_user_id: int,
    reservation_id: int,
    refund_amount: float,
    from_user_id: int | None,
) -> None:
    create_notification(
        db,
        to_user_id=to_user_id,
        type=NotificationType.REFUND_PROCESSED,
        title="退款已处理",
        content=f"预约单 {reservation_id} 退款金额 {refund_amount:.2f} 元。",
        from_user_id=from_user_id,
        meta={
            "reservation_id": reservation_id,
            "refund_amount": refund_amount,
        },
    )


def notify_report_generated(
    db: Session,
    *,
    to_user_id: int,
    report_type: str,
    report_format: str,
    from_user_id: int | None,
) -> None:
    create_notification(
        db,
        to_user_id=to_user_id,
        type=NotificationType.REPORT_GENERATED,
        title="报表生成完成",
        content=f"{report_type}报表已生成，可下载 {report_format.upper()}。",
        from_user_id=from_user_id,
        meta={
            "report_type": report_type,
            "report_format": report_format,
        },
    )


def notify_overdue_reminder(
    db: Session,
    *,
    to_user_id: int,
    reservation_id: int,
    due_time: datetime,
) -> None:
    create_notification(
        db,
        to_user_id=to_user_id,
        type=NotificationType.OVERDUE_REMINDER,
        title="超期提醒",
        content=f"预约单 {reservation_id} 已超过归还时间，请尽快归还设备。",
        from_user_id=None,
        meta={
            "reservation_id": reservation_id,
            "due_time": due_time.isoformat(),
        },
    )

