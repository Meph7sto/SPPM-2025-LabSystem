from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from ...core.errors import AppError, ErrorCode, NotFoundError
from ...core.response import ok
from ...db.session import get_db
from ...models.device import Device
from ...models.finance import FinancePayment, RefundRecord
from ...models.reservation import Reservation, ReservationStatus, PaymentStatus, ApprovalStep
from ...models.user import User, UserRole, BorrowerType
from ...schemas import ReservationCreate, ReservationDetail, ReservationUpdate, ReservationListItem
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/reservations")


def _compute_payment_amount(reservation: Reservation, device: Device) -> float:
    price = float(device.rental_price or 0.0)
    if price <= 0:
        return 0.0
    start = reservation.start_time
    end = reservation.end_time
    try:
        seconds = (end - start).total_seconds()
    except Exception:
        seconds = 0
    hours = max(seconds / 3600.0, 1.0)
    return round(price * hours, 2)


def _ensure_finance_payment(db: Session, reservation: Reservation) -> None:
    """确保校外预约在进入缴费步骤时生成缴费单（T28）。"""
    if reservation.payment_status != PaymentStatus.PENDING:
        return
    if reservation.current_step != ApprovalStep.PAYMENT:
        return
    if not reservation.user or reservation.user.borrower_type != BorrowerType.EXTERNAL:
        return

    finance_payment = db.execute(
        select(FinancePayment).where(FinancePayment.reservation_id == reservation.id)
    ).scalar_one_or_none()

    if not reservation.payment_order_no:
        order_no = f"F-{datetime.utcnow():%Y%m%d}-{reservation.id:06d}"
        reservation.payment_order_no = order_no

    if reservation.payment_amount <= 0:
        device = db.get(Device, reservation.device_id)
        if device:
            reservation.payment_amount = _compute_payment_amount(reservation, device)

    if not finance_payment:
        db.add(
            FinancePayment(
                order_no=reservation.payment_order_no,
                reservation_id=reservation.id,
                amount=reservation.payment_amount,
                status="pending",
            )
        )
    else:
        # 保持订单号与金额一致
        finance_payment.order_no = reservation.payment_order_no
        finance_payment.amount = reservation.payment_amount


def determine_initial_step(borrower_type: BorrowerType | None) -> ApprovalStep:
    """根据借用人类型确定初始审批步骤"""
    if borrower_type == BorrowerType.STUDENT:
        return ApprovalStep.ADVISOR  # 学生先导师审批
    elif borrower_type == BorrowerType.EXTERNAL:
        return ApprovalStep.ADMIN    # 校外先管理员审批
    else:
        return ApprovalStep.ADMIN    # 教师直接管理员审批


def determine_payment_status(borrower_type: BorrowerType | None) -> PaymentStatus:
    """根据借用人类型确定支付状态"""
    if borrower_type == BorrowerType.EXTERNAL:
        return PaymentStatus.PENDING  # 校外人员需要支付
    else:
        return PaymentStatus.NOT_REQUIRED  # 校内人员无需支付


def compute_next_action(reservation: Reservation) -> dict | None:
    """根据当前审批步骤计算下一步动作（用于前端提交审批）"""
    if reservation.status not in [
        ReservationStatus.PENDING,
        ReservationStatus.ADVISOR_APPROVED,
        ReservationStatus.ADMIN_APPROVED,
        ReservationStatus.HEAD_APPROVED,
    ]:
        return None

    step = reservation.current_step
    borrower_type = reservation.user.borrower_type if reservation.user else None

    if step == ApprovalStep.ADVISOR:
        return {
            "status": ReservationStatus.ADVISOR_APPROVED.value,
            "current_step": ApprovalStep.ADMIN.value,
        }
    if step == ApprovalStep.ADMIN:
        if borrower_type == BorrowerType.EXTERNAL:
            return {
                "status": ReservationStatus.ADMIN_APPROVED.value,
                "current_step": ApprovalStep.HEAD.value,
            }
        return {
            "status": ReservationStatus.APPROVED.value,
            "current_step": ApprovalStep.FINAL.value,
        }
    if step == ApprovalStep.HEAD:
        return {
            "status": ReservationStatus.HEAD_APPROVED.value,
            "current_step": ApprovalStep.PAYMENT.value,
        }
    if step == ApprovalStep.PAYMENT:
        return {
            "status": ReservationStatus.APPROVED.value,
            "current_step": ApprovalStep.FINAL.value,
        }
    if step == ApprovalStep.FINAL:
        return {
            "status": ReservationStatus.APPROVED.value,
            "current_step": None,
        }
    return None


@router.post("", response_model=dict)
def create_reservation(
    payload: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """创建新预约申请"""
    # 确定初始审批步骤和支付状态
    initial_step = determine_initial_step(current_user.borrower_type)
    payment_status = determine_payment_status(current_user.borrower_type)
    
    reservation = Reservation(
        user_id=current_user.id,
        status=ReservationStatus.PENDING,
        current_step=initial_step,
        payment_status=payment_status,
        **payload.model_dump()
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return ok(ReservationDetail.model_validate(reservation).model_dump())


@router.get("/{reservation_id}", response_model=dict)
def get_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取预约详情"""
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    
    # 权限检查: 管理员/负责人 或 申请人本人
    if current_user.role not in [UserRole.ADMIN, UserRole.HEAD] and reservation.user_id != current_user.id:
        # 如果是导师，检查是否是其学生的预约
        if current_user.borrower_type == BorrowerType.TEACHER:
            applicant = db.get(User, reservation.user_id)
            if applicant and applicant.advisor_no == current_user.teacher_no:
                pass  # 允许导师查看学生的预约
            else:
                raise AppError(ErrorCode.PERMISSION_DENIED, "无权查看该预约")
        else:
            raise AppError(ErrorCode.PERMISSION_DENIED, "无权查看该预约")

    response = ReservationDetail.model_validate(reservation).model_dump()
    response["next_action"] = compute_next_action(reservation)
    return ok(response)


@router.get("", response_model=dict)
def list_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: ReservationStatus | None = Query(None, description="按状态筛选"),
    device_id: int | None = Query(None, description="按设备筛选"),
    current_step: ApprovalStep | None = Query(None, description="按审批步骤筛选"),
    payment_status: PaymentStatus | None = Query(None, description="按支付状态筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取预约列表"""
    stmt = select(Reservation).options(
        joinedload(Reservation.device),
        joinedload(Reservation.user),
    )
    
    # 权限过滤
    if current_user.role not in [UserRole.ADMIN, UserRole.HEAD]:
        if current_user.borrower_type == BorrowerType.TEACHER:
            # 教师可以看自己的预约 + 其指导学生的预约
            student_ids = db.execute(
                select(User.id).where(User.advisor_no == current_user.teacher_no)
            ).scalars().all()
            stmt = stmt.where(
                (Reservation.user_id == current_user.id) |
                (Reservation.user_id.in_(student_ids))
            )
        else:
            stmt = stmt.where(Reservation.user_id == current_user.id)
    
    # 条件筛选
    if status:
        stmt = stmt.where(Reservation.status == status)
    if device_id:
        stmt = stmt.where(Reservation.device_id == device_id)
    if current_step is not None:
        stmt = stmt.where(Reservation.current_step == current_step)
    if payment_status is not None:
        stmt = stmt.where(Reservation.payment_status == payment_status)
    
    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # 分页并排序
    stmt = stmt.order_by(Reservation.created_at.desc()).offset(skip).limit(limit)
    reservations = db.execute(stmt).scalars().all()
    
    items = []
    for reservation in reservations:
        item = ReservationListItem.model_validate(reservation).model_dump()
        item["next_action"] = compute_next_action(reservation)
        items.append(item)

    return ok({
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    })


@router.post("/{reservation_id}/payment/sync", response_model=dict)
def sync_payment_status(
    reservation_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """从财务系统同步缴费确认（T29）。"""
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    if not reservation.payment_order_no:
        raise AppError(ErrorCode.INVALID_REQUEST, "该预约未生成缴费单")

    fp = db.execute(
        select(FinancePayment).where(FinancePayment.order_no == reservation.payment_order_no)
    ).scalar_one_or_none()
    if not fp:
        raise NotFoundError(f"缴费单不存在 (order_no={reservation.payment_order_no})")

    if fp.status == "paid":
        reservation.payment_status = PaymentStatus.PAID
        reservation.payment_time = fp.paid_time
        if reservation.current_step == ApprovalStep.PAYMENT:
            reservation.status = ReservationStatus.APPROVED
            reservation.current_step = ApprovalStep.FINAL

    db.commit()
    db.refresh(reservation)
    return ok(ReservationDetail.model_validate(reservation).model_dump(), message="已同步财务状态")


@router.post("/{reservation_id}/finalize", response_model=dict)
def finalize_reservation(
    reservation_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> dict:
    """管理员最终确认：缴费确认成功后才能进入“已生效/可借出”（T32）。"""
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")

    if reservation.current_step != ApprovalStep.FINAL:
        raise AppError(ErrorCode.INVALID_REQUEST, "当前预约不在最终确认步骤")

    if reservation.user and reservation.user.borrower_type == BorrowerType.EXTERNAL:
        if reservation.payment_status != PaymentStatus.PAID:
            raise AppError(ErrorCode.INVALID_REQUEST, "校外预约必须缴费成功后才能最终确认")

    reservation.status = ReservationStatus.EFFECTIVE
    reservation.current_step = None
    db.commit()
    db.refresh(reservation)
    return ok(ReservationDetail.model_validate(reservation).model_dump(), message="最终确认成功")


@router.post("/{reservation_id}/cancel", response_model=dict)
def cancel_reservation_with_refund(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """撤销预约：若已付费则按 95% 自动退款并生成退款记录（T33）。"""
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")

    is_admin = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_owner = reservation.user_id == current_user.id
    if not (is_admin or is_owner):
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权撤销该预约")

    if reservation.status in [ReservationStatus.BORROWED, ReservationStatus.COMPLETED]:
        raise AppError(ErrorCode.INVALID_REQUEST, "已借出/已完成的预约不能撤销")

    refund_amount = 0.0
    if reservation.payment_status == PaymentStatus.PAID and (reservation.payment_amount or 0) > 0:
        refund_amount = round(float(reservation.payment_amount) * 0.95, 2)
        reservation.payment_status = PaymentStatus.REFUNDED
        reservation.refund_amount = refund_amount
        reservation.refund_time = datetime.utcnow()

        db.add(
            RefundRecord(
                reservation_id=reservation.id,
                order_no=reservation.payment_order_no,
                original_amount=float(reservation.payment_amount),
                refund_rate=0.95,
                refund_amount=refund_amount,
                status="processed",
            )
        )

        # 同步更新财务侧订单状态（Mock）
        fp = None
        if reservation.payment_order_no:
            fp = db.execute(
                select(FinancePayment).where(FinancePayment.order_no == reservation.payment_order_no)
            ).scalar_one_or_none()
        if fp:
            fp.status = "refunded"

    reservation.status = ReservationStatus.CANCELLED
    reservation.current_step = None
    db.commit()
    db.refresh(reservation)
    return ok(
        {
            "reservation": ReservationDetail.model_validate(reservation).model_dump(),
            "refund_amount": refund_amount,
        },
        message="预约已撤销" if refund_amount == 0 else "预约已撤销并退款",
    )


@router.put("/{reservation_id}", response_model=dict)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """更新预约信息"""
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_owner = reservation.user_id == current_user.id
    
    if not (is_admin or is_owner):
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权修改该预约")
        
    update_data = payload.model_dump(exclude_unset=True)
    
    if not is_admin:
        # 申请人限制
        # 只能在待审批或退回补充材料状态下修改
        if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.RETURNED]:
            raise AppError(ErrorCode.INVALID_REQUEST, "当前状态不允许修改")
        
        # 申请人只能取消或修改描述/时间
        allowed_fields = {"start_time", "end_time", "description", "status", "contact"}
        for key in list(update_data.keys()):
            if key not in allowed_fields:
                del update_data[key]
        
        # 只能取消
        if "status" in update_data and update_data["status"] != ReservationStatus.CANCELLED:
            raise AppError(ErrorCode.PERMISSION_DENIED, "只能取消预约")

    for key, value in update_data.items():
        setattr(reservation, key, value)

    # T28: 校外预约进入缴费步骤时生成缴费单
    _ensure_finance_payment(db, reservation)
    
    db.commit()
    db.refresh(reservation)
    return ok(ReservationDetail.model_validate(reservation).model_dump())


@router.delete("/{reservation_id}", response_model=dict)
def delete_reservation(
    reservation_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """删除预约（管理员/负责人）"""
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    
    db.delete(reservation)
    db.commit()
    return ok({"id": reservation_id}, message="预约删除成功")


# ==================== 台账查询接口 ====================

@router.get("/ledger/summary", response_model=dict)
def get_reservation_ledger_summary(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取预约台账统计摘要（管理员/负责人）"""
    # 按状态统计
    status_counts = {}
    for status in ReservationStatus:
        count = db.execute(
            select(func.count()).where(Reservation.status == status)
        ).scalar() or 0
        status_counts[status.value] = count
    
    # 按支付状态统计
    payment_counts = {}
    for pstatus in PaymentStatus:
        count = db.execute(
            select(func.count()).where(Reservation.payment_status == pstatus)
        ).scalar() or 0
        payment_counts[pstatus.value] = count
    
    total = db.execute(select(func.count()).select_from(Reservation)).scalar() or 0
    
    return ok({
        "total": total,
        "by_status": status_counts,
        "by_payment_status": payment_counts,
    })
