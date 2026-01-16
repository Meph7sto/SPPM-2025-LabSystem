from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.errors import AppError, ErrorCode, NotFoundError
from ...core.response import ok
from ...db.session import get_db
from ...models.finance import FinancePayment
from ...models.reservation import Reservation, PaymentStatus
from ...models.user import UserRole
from ..deps import require_roles
from ...services.notifications import notify_payment_confirmed


router = APIRouter(prefix="/finance")


class FinancePaymentOut(BaseModel):
    order_no: str
    reservation_id: int
    amount: float
    status: str
    paid_time: datetime | None = None


class FinanceUpdateIn(BaseModel):
    status: str = Field(..., description="pending/paid/failed")
    paid_time: datetime | None = None


class FinanceCallbackIn(BaseModel):
    order_no: str
    status: str = Field(..., description="pending/paid/failed")
    paid_time: datetime | None = None


def _normalize_status(value: str) -> str:
    v = (value or "").strip().lower()
    if v in {"pending", "paid", "failed"}:
        return v
    raise AppError(ErrorCode.VALIDATION_ERROR, "status 必须为 pending/paid/failed")


def _apply_finance_status_to_reservation(
    db: Session,
    reservation: Reservation,
    finance_payment: FinancePayment,
    status: str,
    paid_time: datetime | None,
) -> None:
    # 财务状态写入财务表
    finance_payment.status = status
    finance_payment.paid_time = paid_time

    # 仅在缴费成功时更新支付信息
    if status == "paid":
        reservation.payment_status = PaymentStatus.PAID
        reservation.payment_time = paid_time
        notify_payment_confirmed(
            db,
            to_user_id=reservation.user_id,
            reservation_id=reservation.id,
            order_no=finance_payment.order_no,
        )


@router.get("/payments/{order_no}", response_model=dict)
def get_finance_payment(
    order_no: str,
    current_user=Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    fp = db.execute(select(FinancePayment).where(FinancePayment.order_no == order_no)).scalar_one_or_none()
    if not fp:
        raise NotFoundError(f"缴费单不存在 (order_no={order_no})")
    data = FinancePaymentOut(
        order_no=fp.order_no,
        reservation_id=fp.reservation_id,
        amount=fp.amount,
        status=fp.status,
        paid_time=fp.paid_time,
    ).model_dump()
    return ok(data)


@router.post("/mock/payments/{order_no}", response_model=dict)
def mock_update_finance_payment(
    order_no: str,
    payload: FinanceUpdateIn,
    current_user=Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    if not settings.finance_mock_enabled:
        raise AppError(ErrorCode.FORBIDDEN, "财务 Mock 未启用", status_code=403)

    status = _normalize_status(payload.status)
    paid_time = payload.paid_time
    if status == "paid" and not paid_time:
        paid_time = datetime.now(timezone.utc)

    fp = db.execute(select(FinancePayment).where(FinancePayment.order_no == order_no)).scalar_one_or_none()
    if not fp:
        raise NotFoundError(f"缴费单不存在 (order_no={order_no})")

    reservation = db.get(Reservation, fp.reservation_id)
    if not reservation:
        raise NotFoundError(f"关联预约不存在 (id={fp.reservation_id})")

    _apply_finance_status_to_reservation(db, reservation, fp, status, paid_time)
    db.commit()
    db.refresh(fp)

    return ok({
        "order_no": fp.order_no,
        "status": fp.status,
        "paid_time": fp.paid_time.isoformat() if fp.paid_time else None,
        "reservation_id": fp.reservation_id,
    }, message="Mock 财务状态已更新")


@router.post("/callback", response_model=dict)
def finance_callback(
    payload: FinanceCallbackIn,
    db: Session = Depends(get_db),
) -> dict:
    """财务系统回调入口（IR-EXT-1）。

    为便于演示：默认仅在 FINANCE_MOCK_ENABLED=true 时放行。
    """
    if not settings.finance_mock_enabled:
        raise AppError(ErrorCode.FORBIDDEN, "财务回调未启用", status_code=403)

    status = _normalize_status(payload.status)
    paid_time = payload.paid_time
    if status == "paid" and not paid_time:
        paid_time = datetime.now(timezone.utc)

    fp = db.execute(select(FinancePayment).where(FinancePayment.order_no == payload.order_no)).scalar_one_or_none()
    if not fp:
        raise NotFoundError(f"缴费单不存在 (order_no={payload.order_no})")
    reservation = db.get(Reservation, fp.reservation_id)
    if not reservation:
        raise NotFoundError(f"关联预约不存在 (id={fp.reservation_id})")

    _apply_finance_status_to_reservation(db, reservation, fp, status, paid_time)
    db.commit()
    return ok({"order_no": payload.order_no, "status": status})
