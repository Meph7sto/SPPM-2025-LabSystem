from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session, joinedload

from ...core.errors import AppError, ErrorCode, NotFoundError
from ...core.response import ok
from ...db.session import get_db
from ...models.device import Device, DeviceStatus
from ...models.finance import FinancePayment, RefundRecord
from ...models.maintenance_window import MaintenanceWindow
from ...models.reservation import Reservation, ReservationStatus, PaymentStatus, ApprovalStep
from ...models.user import User, UserRole, BorrowerType
from ...schemas import ReservationCreate, ReservationDetail, ReservationUpdate, ReservationListItem, BorrowRequest, ReturnRequest
from ...services.notifications import (
    notify_approval_result,
    notify_payment_confirmed,
    notify_submit_success,
    notify_refund_processed,
    notify_reservation_cancelled,
)
from ...services.reservation_pdf import generate_reservation_pdf
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/reservations")

ACTIVE_CONFLICT_STATUSES = [
    ReservationStatus.PENDING,
    ReservationStatus.ADVISOR_APPROVED,
    ReservationStatus.ADMIN_APPROVED,
    ReservationStatus.HEAD_APPROVED,
    ReservationStatus.APPROVED,
    ReservationStatus.EFFECTIVE,
    ReservationStatus.BORROWED,
]

ACTIVE_STATUS_VALUES = {status.value for status in ACTIVE_CONFLICT_STATUSES}

BLOCKING_CONFLICT_STATUSES = [
    ReservationStatus.APPROVED,
    ReservationStatus.EFFECTIVE,
    ReservationStatus.BORROWED,
]

BLOCKING_STATUS_VALUES = {status.value for status in BLOCKING_CONFLICT_STATUSES}

PRIORITY_CONFLICT_STATUSES = [
    ReservationStatus.PENDING,
    ReservationStatus.ADVISOR_APPROVED,
    ReservationStatus.ADMIN_APPROVED,
    ReservationStatus.HEAD_APPROVED,
]

PRIORITY_DECISION_STATUS_VALUES = {
    ReservationStatus.ADVISOR_APPROVED.value,
    ReservationStatus.ADMIN_APPROVED.value,
    ReservationStatus.HEAD_APPROVED.value,
    ReservationStatus.APPROVED.value,
    ReservationStatus.EFFECTIVE.value,
}


def _begin_reservation_transaction(db: Session) -> None:
    """确保在冲突校验前获取写锁，避免并发双占用。"""
    engine = db.get_bind()
    if engine.dialect.name != "sqlite":
        return
    if db.in_transaction():
        db.rollback()
    try:
        db.execute(text("BEGIN IMMEDIATE"))
    except Exception as exc:
        raise AppError(ErrorCode.CONFLICT, "系统繁忙，请稍后再试") from exc


def _lock_device(db: Session, device_id: int) -> None:
    """在支持行级锁的数据库中锁定设备行。"""
    engine = db.get_bind()
    if engine.dialect.name == "sqlite":
        return
    db.execute(
        select(Device.id)
        .where(Device.id == device_id)
        .with_for_update()
    )


def _count_conflicts(
    db: Session,
    device_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_id: int | None = None,
    statuses: list[ReservationStatus] | None = None,
) -> int:
    stmt = select(func.count()).select_from(Reservation).where(
        Reservation.device_id == device_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )
    if exclude_id is not None:
        stmt = stmt.where(Reservation.id != exclude_id)
    if statuses:
        stmt = stmt.where(Reservation.status.in_(statuses))
    return int(db.execute(stmt).scalar() or 0)


def _ensure_no_blocking_conflict(
    db: Session,
    device_id: int,
    start_time: datetime,
    end_time: datetime,
    exclude_id: int | None = None,
) -> None:
    conflict_count = _count_conflicts(
        db,
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        exclude_id=exclude_id,
        statuses=BLOCKING_CONFLICT_STATUSES,
    )
    if conflict_count:
        raise AppError(ErrorCode.CONFLICT, "该设备在该时段已被占用，请调整时间或处理冲突预约")


def _count_maintenance_conflicts(
    db: Session,
    device_id: int,
    start_time: datetime,
    end_time: datetime,
) -> int:
    stmt = select(func.count()).select_from(MaintenanceWindow).where(
        MaintenanceWindow.device_id == device_id,
        MaintenanceWindow.start_time < end_time,
        MaintenanceWindow.end_time > start_time,
    )
    return int(db.execute(stmt).scalar() or 0)


def _ensure_no_maintenance_conflict(
    db: Session,
    device_id: int,
    start_time: datetime,
    end_time: datetime,
) -> None:
    if _count_maintenance_conflicts(db, device_id, start_time, end_time):
        raise AppError(ErrorCode.CONFLICT, "该设备处于检修时间窗内，无法预约")


def _build_conflict_info(db: Session, reservation: Reservation) -> dict:
    conflict_count = _count_conflicts(
        db,
        device_id=reservation.device_id,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
        exclude_id=reservation.id,
        statuses=ACTIVE_CONFLICT_STATUSES,
    )
    return {
        "conflict": conflict_count > 0,
        "conflict_count": conflict_count,
    }


def _priority_level(user: User | None) -> int:
    if user and user.borrower_type == BorrowerType.EXTERNAL:
        return 2
    return 1


def _priority_info(user: User | None) -> dict:
    level = _priority_level(user)
    if level == 2:
        return {"priority": "校外缴费", "priority_level": level}
    return {"priority": "校内优先", "priority_level": level}


def _fetch_priority_conflicts(db: Session, reservation: Reservation) -> list[Reservation]:
    stmt = (
        select(Reservation)
        .options(joinedload(Reservation.user))
        .where(
            Reservation.device_id == reservation.device_id,
            Reservation.start_time < reservation.end_time,
            Reservation.end_time > reservation.start_time,
            Reservation.id != reservation.id,
            Reservation.status.in_(PRIORITY_CONFLICT_STATUSES),
        )
    )
    return db.execute(stmt).scalars().all()


def _auto_reject_reservation(
    db: Session,
    reservation: Reservation,
    *,
    actor_user_id: int | None,
    reason: str,
    notify: bool,
) -> None:
    reservation.status = ReservationStatus.REJECTED
    reservation.current_step = None
    if not reservation.approval_comment:
        reservation.approval_comment = reason
    if notify and reservation.user_id:
        notify_approval_result(
            db,
            to_user_id=reservation.user_id,
            reservation_id=reservation.id,
            status="rejected",
            from_user_id=actor_user_id,
        )


def _apply_priority_resolution(
    db: Session,
    reservation: Reservation,
    *,
    actor_user_id: int | None,
) -> bool:
    user = reservation.user or db.get(User, reservation.user_id)
    reservation.user = user
    current_level = _priority_level(user)
    conflicts = _fetch_priority_conflicts(db, reservation)
    if not conflicts:
        return False

    higher_priority = [
        conflict for conflict in conflicts if _priority_level(conflict.user) < current_level
    ]
    if higher_priority:
        _auto_reject_reservation(
            db,
            reservation,
            actor_user_id=actor_user_id,
            reason="系统自动驳回：校内预约优先",
            notify=False,
        )
        return True

    lower_priority = [
        conflict for conflict in conflicts if _priority_level(conflict.user) > current_level
    ]
    for conflict in lower_priority:
        _auto_reject_reservation(
            db,
            conflict,
            actor_user_id=actor_user_id,
            reason="系统自动驳回：校内预约优先",
            notify=True,
        )
    return False



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
    """
    根据借用人类型确定初始审批步骤。

    - 学生 -> 导师审批
    - 校外人员 -> 管理员审批 (随后可能需要负责人审批)
    - 教师 -> 管理员审批
    """
    if borrower_type == BorrowerType.STUDENT:
        return ApprovalStep.ADVISOR
    elif borrower_type == BorrowerType.EXTERNAL:
        return ApprovalStep.ADMIN
    else:
        return ApprovalStep.ADMIN


def determine_payment_status(borrower_type: BorrowerType | None) -> PaymentStatus:
    """
    根据借用人类型确定初始支付状态。

    - 校外人员 -> 待支付 (需走付费流程)
    - 校内人员 -> 无需支付
    """
    if borrower_type == BorrowerType.EXTERNAL:
        return PaymentStatus.PENDING
    else:
        return PaymentStatus.NOT_REQUIRED


def compute_next_action(reservation: Reservation) -> dict | None:
    """
    计算当前预约单的下一步审批动作（用于前端显示和引导）。

    根据当前状态和步骤，预测如果当前步骤通过，下一个状态是什么。

    Returns:
        dict: 包含 'status' 和 'current_step' 的字典，表示下一步的状态。
    """
    # 只有在进行中的状态才需要计算下一步
    if reservation.status not in [
        ReservationStatus.PENDING,
        ReservationStatus.ADVISOR_APPROVED,
        ReservationStatus.ADMIN_APPROVED,
        ReservationStatus.HEAD_APPROVED,
    ]:
        return None

    step = reservation.current_step
    borrower_type = reservation.user.borrower_type if reservation.user else None

    # 1. 导师审批 -> 管理员审批
    if step == ApprovalStep.ADVISOR:
        return {
            "status": ReservationStatus.ADVISOR_APPROVED.value,
            "current_step": ApprovalStep.ADMIN.value,
        }
    # 2. 管理员审批
    if step == ApprovalStep.ADMIN:
        if borrower_type == BorrowerType.EXTERNAL:
            # 校外人员：管理员 -> 负责人
            return {
                "status": ReservationStatus.ADMIN_APPROVED.value,
                "current_step": ApprovalStep.HEAD.value,
            }
        # 校内人员：管理员 -> 终审 (直接通过)
        return {
            "status": ReservationStatus.APPROVED.value,
            "current_step": ApprovalStep.FINAL.value,
        }
    # 3. 负责人审批 -> 支付/终审
    if step == ApprovalStep.HEAD:
        # 简化逻辑：负责人审批通过后进入支付环节
        return {
            "status": ReservationStatus.HEAD_APPROVED.value,
            "current_step": ApprovalStep.PAYMENT.value,
        }
    # 4. 支付环节 -> 终审
    if step == ApprovalStep.PAYMENT:
        return {
            "status": ReservationStatus.APPROVED.value,
            "current_step": ApprovalStep.FINAL.value,
        }
    # 5. 终审环节 -> 结束 (Approved)
    if step == ApprovalStep.FINAL:
        return {
            "status": ReservationStatus.APPROVED.value,
            "current_step": None,
        }
    return None


def _update_device_status_on_borrow(db: Session, device_id: int) -> None:
    """T36: 借出时更新设备状态为使用中。"""
    device = db.get(Device, device_id)
    if device and device.status != DeviceStatus.SCRAPPED:
        device.status = DeviceStatus.IN_USE


def _update_device_status_on_return(
    db: Session,
    device_id: int,
    condition: str,
) -> None:
    """T36: 归还时根据设备状态更新设备。"""
    device = db.get(Device, device_id)
    if not device or device.status == DeviceStatus.SCRAPPED:
        return
    
    if condition == "normal":
        device.status = DeviceStatus.IDLE
    elif condition in ["damaged", "needs_maintenance"]:
        device.status = DeviceStatus.MAINTENANCE
    else:
        # 默认恢复为空闲状态
        device.status = DeviceStatus.IDLE


@router.post("", response_model=dict)
def create_reservation(
    payload: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    创建新预约申请。
    自动初始化审批流程状态。
    """
    _begin_reservation_transaction(db)
    # T15 规则校验：检查设备是否存在与状态
    device = db.get(Device, payload.device_id)
    if not device:
        raise NotFoundError(f"设备不存在 (id={payload.device_id})")
    if device.status == "maintenance":  # DeviceStatus.MAINTENANCE.value
        raise AppError(ErrorCode.CONFLICT, "设备正在维修中，暂停借用")
    if device.status == "scrapped":
        raise AppError(ErrorCode.CONFLICT, "设备已报废，无法借用")

    # T15 规则校验：时间规则
    # 1. 必须提前1-7天预约
    now = datetime.now(payload.start_time.tzinfo) if payload.start_time.tzinfo else datetime.now()
    min_start_time = now + timedelta(days=1)
    max_start_time = now + timedelta(days=7)
    
    if payload.start_time < min_start_time:
         raise AppError(ErrorCode.INVALID_REQUEST, "必须至少提前1天预约")
    if payload.start_time > max_start_time:
         raise AppError(ErrorCode.INVALID_REQUEST, "只能预约未来7天内的时间")

    # 2. 借用时间单位为2小时 (即整除2小时, 且至少2小时)
    duration = payload.end_time - payload.start_time
    duration_seconds = duration.total_seconds()
    if duration_seconds < 7200:
        raise AppError(ErrorCode.INVALID_REQUEST, "借用时间至少为2小时")
    if duration_seconds % 7200 != 0:
        raise AppError(ErrorCode.INVALID_REQUEST, "借用时间必须是2小时的整数倍")

    _ensure_no_maintenance_conflict(
        db,
        payload.device_id,
        payload.start_time,
        payload.end_time,
    )
    _lock_device(db, payload.device_id)
    _ensure_no_blocking_conflict(db, payload.device_id, payload.start_time, payload.end_time)

    # 1. 确定初始状态
    initial_step = determine_initial_step(current_user.borrower_type)
    payment_status = determine_payment_status(current_user.borrower_type)
    
    # 2. 创建记录
    reservation = Reservation(
        user_id=current_user.id,
        status=ReservationStatus.PENDING,
        current_step=initial_step,
        payment_status=payment_status,
        **payload.model_dump()
    )
    db.add(reservation)
    db.flush()
    notify_submit_success(db, user_id=current_user.id, reservation_id=reservation.id)
    db.commit()
    db.refresh(reservation)
    response = ReservationDetail.model_validate(reservation).model_dump()
    response.update(_build_conflict_info(db, reservation))
    response.update(_priority_info(reservation.user))
    return ok(response)


@router.get("/{reservation_id}", response_model=dict)
def get_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    获取预约详情。

    包含权限检查：
    - 管理员/负责人：可查看所有
    - 申请人：可查看自己申请的
    - 导师：可查看自己指导学生的申请
    """
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    
    # 权限检查
    if current_user.role not in [UserRole.ADMIN, UserRole.HEAD] and reservation.user_id != current_user.id:
        # 特殊逻辑：导师查看学生
        if current_user.borrower_type == BorrowerType.TEACHER:
            applicant = db.get(User, reservation.user_id)
            if applicant and applicant.advisor_no == current_user.teacher_no:
                pass  # 允许
            else:
                raise AppError(ErrorCode.PERMISSION_DENIED, "无权查看该预约")
        else:
            raise AppError(ErrorCode.PERMISSION_DENIED, "无权查看该预约")

    response = ReservationDetail.model_validate(reservation).model_dump()
    response["next_action"] = compute_next_action(reservation)
    response.update(_build_conflict_info(db, reservation))
    response.update(_priority_info(reservation.user))
    return ok(response)


@router.get("/{reservation_id}/export/pdf")
def export_reservation_pdf(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    导出预约单 PDF。
    - 申请人可导出自己的预约
    - 导师可导出自己学生的预约
    - 管理员/负责人可导出所有
    """
    reservation = db.execute(
        select(Reservation)
        .options(
            joinedload(Reservation.device),
            joinedload(Reservation.user),
            joinedload(Reservation.advisor),
            joinedload(Reservation.approver),
            joinedload(Reservation.head),
        )
        .where(Reservation.id == reservation_id)
    ).scalar_one_or_none()

    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")

    # 权限检查（与 get_reservation 保持一致）
    if current_user.role not in [UserRole.ADMIN, UserRole.HEAD] and reservation.user_id != current_user.id:
        if current_user.borrower_type == BorrowerType.TEACHER:
            applicant = db.get(User, reservation.user_id)
            if not (applicant and applicant.advisor_no == current_user.teacher_no):
                raise AppError(ErrorCode.PERMISSION_DENIED, "无权导出该预约")
        else:
            raise AppError(ErrorCode.PERMISSION_DENIED, "无权导出该预约")

    pdf_bytes = generate_reservation_pdf(reservation)
    filename = f"reservation-{reservation.id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'},
    )

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
    """
    获取预约列表。

    根据用户角色自动过滤：
    - 管理员/负责人：查看所有（可筛选）
    - 教师：查看自己 + 指导的学生
    - 学生/校外：仅查看自己
    """
    stmt = select(Reservation).options(
        joinedload(Reservation.device),
        joinedload(Reservation.user),
    )
    
    # 权限过滤
    if current_user.role not in [UserRole.ADMIN, UserRole.HEAD]:
        if current_user.borrower_type == BorrowerType.TEACHER:
            # 教师视角：自己 + 学生
            student_ids = db.execute(
                select(User.id).where(User.advisor_no == current_user.teacher_no)
            ).scalars().all()
            stmt = stmt.where(
                (Reservation.user_id == current_user.id) |
                (Reservation.user_id.in_(student_ids))
            )
        else:
            # 普通视角：仅自己
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
    
    # 分页并排序 (最新优先)
    stmt = stmt.order_by(Reservation.created_at.desc()).offset(skip).limit(limit)
    reservations = db.execute(stmt).scalars().all()
    
    items = []
    for reservation in reservations:
        item = ReservationListItem.model_validate(reservation).model_dump()
        item["next_action"] = compute_next_action(reservation)
        item.update(_build_conflict_info(db, reservation))
        item.update(_priority_info(reservation.user))
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
    _begin_reservation_transaction(db)
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    _lock_device(db, reservation.device_id)
    if not reservation.payment_order_no:
        raise AppError(ErrorCode.INVALID_REQUEST, "该预约未生成缴费单")

    fp = db.execute(
        select(FinancePayment).where(FinancePayment.order_no == reservation.payment_order_no)
    ).scalar_one_or_none()
    if not fp:
        raise NotFoundError(f"缴费单不存在 (order_no={reservation.payment_order_no})")

    old_payment_status = reservation.payment_status
    if fp.status == "paid":
        _ensure_no_blocking_conflict(
            db,
            reservation.device_id,
            reservation.start_time,
            reservation.end_time,
            exclude_id=reservation.id,
        )
        _ensure_no_maintenance_conflict(
            db,
            reservation.device_id,
            reservation.start_time,
            reservation.end_time,
        )
        reservation.payment_status = PaymentStatus.PAID
        reservation.payment_time = fp.paid_time
        if reservation.current_step == ApprovalStep.PAYMENT:
            reservation.status = ReservationStatus.APPROVED
            reservation.current_step = ApprovalStep.FINAL
        if old_payment_status != PaymentStatus.PAID:
            notify_payment_confirmed(
                db,
                to_user_id=reservation.user_id,
                reservation_id=reservation.id,
                order_no=reservation.payment_order_no,
            )

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
    _begin_reservation_transaction(db)
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    _lock_device(db, reservation.device_id)

    if reservation.current_step != ApprovalStep.FINAL:
        raise AppError(ErrorCode.INVALID_REQUEST, "当前预约不在最终确认步骤")

    if reservation.user and reservation.user.borrower_type == BorrowerType.EXTERNAL:
        if reservation.payment_status != PaymentStatus.PAID:
            raise AppError(ErrorCode.INVALID_REQUEST, "校外预约必须缴费成功后才能最终确认")

    _ensure_no_blocking_conflict(
        db,
        reservation.device_id,
        reservation.start_time,
        reservation.end_time,
        exclude_id=reservation.id,
    )
    _ensure_no_maintenance_conflict(
        db,
        reservation.device_id,
        reservation.start_time,
        reservation.end_time,
    )

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

    # T15 规则校验：已经批准的预约可以撤销(至少提前1天以上)
    now = datetime.now(reservation.start_time.tzinfo) if reservation.start_time.tzinfo else datetime.now()
    if reservation.start_time - now < timedelta(days=1):
         raise AppError(ErrorCode.INVALID_REQUEST, "距离预约开始时间不足1天，无法撤销")

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

    notify_reservation_cancelled(
        db,
        to_user_id=reservation.user_id,
        reservation_id=reservation.id,
        from_user_id=current_user.id,
    )
    if refund_amount > 0:
        notify_refund_processed(
            db,
            to_user_id=reservation.user_id,
            reservation_id=reservation.id,
            refund_amount=refund_amount,
            from_user_id=current_user.id,
        )
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
    """
    更新预约信息。

    普通用户（申请人）仅能：
    1. 在待审批或退回状态下修改时间/描述。
    2. 在待审批或退回状态下取消预约。

    管理员/负责人：
    1. 拥有完全修改权限。
    """
    _begin_reservation_transaction(db)
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    _lock_device(db, reservation.device_id)
    
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_owner = reservation.user_id == current_user.id
    old_status = reservation.status
    
    if not (is_admin or is_owner):
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权修改该预约")
        
    update_data = payload.model_dump(exclude_unset=True)
    
    if not is_admin:
        # 普通用户限制逻辑
        # 1. 只能在 PENDING 或 RETURNED 状态修改
        if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.RETURNED]:
            raise AppError(ErrorCode.INVALID_REQUEST, "当前状态不允许修改")
        
        # 2. 字段白名单过滤
        allowed_fields = {"start_time", "end_time", "description", "status", "contact"}
        for key in list(update_data.keys()):
            if key not in allowed_fields:
                del update_data[key]
        
        # 3. 状态限制：只能改为 CANCELLED
        if "status" in update_data and update_data["status"] != ReservationStatus.CANCELLED:
            raise AppError(ErrorCode.PERMISSION_DENIED, "只能执行取消操作")

    # 执行更新
    for key, value in update_data.items():
        setattr(reservation, key, value)

    target_status = update_data.get("status", reservation.status)
    target_status_value = target_status.value if isinstance(target_status, ReservationStatus) else str(target_status)
    target_start = update_data.get("start_time", reservation.start_time)
    target_end = update_data.get("end_time", reservation.end_time)
    should_check_conflict = (
        "start_time" in update_data
        or "end_time" in update_data
        or target_status_value in BLOCKING_STATUS_VALUES
    )
    if should_check_conflict and target_status_value != ReservationStatus.CANCELLED.value:
        _ensure_no_blocking_conflict(
            db,
            reservation.device_id,
            target_start,
            target_end,
            exclude_id=reservation.id,
        )

    maintenance_check = (
        "start_time" in update_data
        or "end_time" in update_data
        or (reservation.status != old_status and target_status_value in ACTIVE_STATUS_VALUES)
    )
    if maintenance_check and target_status_value not in [
        ReservationStatus.CANCELLED.value,
        ReservationStatus.REJECTED.value,
        ReservationStatus.RETURNED.value,
    ]:
        _ensure_no_maintenance_conflict(
            db,
            reservation.device_id,
            target_start,
            target_end,
        )

    priority_rejected = False
    if reservation.status != old_status and target_status_value in PRIORITY_DECISION_STATUS_VALUES:
        priority_rejected = _apply_priority_resolution(
            db,
            reservation,
            actor_user_id=current_user.id if current_user else None,
        )

    # T28: 校外预约进入缴费步骤时生成缴费单
    if not priority_rejected and reservation.status != ReservationStatus.REJECTED:
        _ensure_finance_payment(db, reservation)
    
    # 审批结果通知
    if reservation.status != old_status:
        status_flag = None
        if reservation.status == ReservationStatus.APPROVED:
            status_flag = "approved"
        elif reservation.status == ReservationStatus.REJECTED:
            status_flag = "rejected"
        elif reservation.status == ReservationStatus.RETURNED:
            status_flag = "returned"
        if status_flag:
            notify_approval_result(
                db,
                to_user_id=reservation.user_id,
                reservation_id=reservation.id,
                status=status_flag,
                from_user_id=current_user.id,
            )

    db.commit()
    db.refresh(reservation)
    response = ReservationDetail.model_validate(reservation).model_dump()
    response.update(_build_conflict_info(db, reservation))
    response.update(_priority_info(reservation.user))
    return ok(response, message="预约更新成功")


@router.delete("/{reservation_id}", response_model=dict)
def delete_reservation(
    reservation_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """
    删除预约记录（仅管理员/负责人）。
    慎用，通常建议使用取消或归档代替物理删除。
    """
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    
    db.delete(reservation)
    db.commit()
    return ok({"id": reservation_id}, message="预约删除成功")


# ==================== 台账查询接口 ====================

@router.post("/{reservation_id}/borrow", response_model=dict)
def borrow_equipment(
    reservation_id: int,
    payload: BorrowRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> dict:
    """
    借出登记（T34 / FR-25）。
    
    仅管理员可操作。要求预约必须处于 EFFECTIVE（已生效）状态。
    操作完成后：
    1. 记录借出时间 (borrow_time)
    2. 记录交接备注 (handover_note)
    3. 更新预约状态为 BORROWED（已借出）
    4. 更新设备状态为 IN_USE（使用中）- T36
    """
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    
    # 验证预约状态：必须是已生效
    if reservation.status != ReservationStatus.EFFECTIVE:
        raise AppError(
            ErrorCode.INVALID_REQUEST,
            f"预约状态必须为已生效才能借出，当前状态：{reservation.status.value}"
        )
    
    # 验证设备存在
    device = db.get(Device, reservation.device_id)
    if not device:
        raise NotFoundError(f"设备不存在 (id={reservation.device_id})")
    
    if device.status == DeviceStatus.SCRAPPED:
        raise AppError(ErrorCode.INVALID_REQUEST, "设备已报废，无法借出")
    
    # 记录借出信息
    reservation.borrow_time = datetime.utcnow()
    reservation.handover_note = payload.handover_note
    reservation.status = ReservationStatus.BORROWED
    
    # T36: 更新设备状态为使用中
    _update_device_status_on_borrow(db, reservation.device_id)
    
    db.commit()
    db.refresh(reservation)
    
    return ok(
        ReservationDetail.model_validate(reservation).model_dump(),
        message="借出登记成功"
    )


@router.post("/{reservation_id}/return", response_model=dict)
def return_equipment(
    reservation_id: int,
    payload: ReturnRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> dict:
    """
    归还登记（T35 / FR-26）。
    
    仅管理员可操作。要求预约必须处于 BORROWED（已借出）状态。
    操作完成后：
    1. 记录归还时间 (return_time)
    2. 记录归还备注 (return_note)
    3. 更新预约状态为 COMPLETED（已完成）
    4. 根据设备状态更新设备：
       - normal: IDLE（空闲）
       - damaged/needs_maintenance: MAINTENANCE（检修中）- T36
    """
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError(f"预约不存在 (id={reservation_id})")
    
    # 验证预约状态：必须是已借出
    if reservation.status != ReservationStatus.BORROWED:
        raise AppError(
            ErrorCode.INVALID_REQUEST,
            f"预约状态必须为已借出才能归还，当前状态：{reservation.status.value}"
        )
    
    # 验证设备状态选项
    valid_conditions = ["normal", "damaged", "needs_maintenance"]
    if payload.device_condition not in valid_conditions:
        raise AppError(
            ErrorCode.INVALID_REQUEST,
            f"设备状态无效，必须为：{', '.join(valid_conditions)}"
        )
    
    # 验证设备存在
    device = db.get(Device, reservation.device_id)
    if not device:
        raise NotFoundError(f"设备不存在 (id={reservation.device_id})")
    
    # 记录归还信息
    reservation.return_time = datetime.utcnow()
    reservation.return_note = payload.return_note
    reservation.status = ReservationStatus.COMPLETED
    
    # T36: 根据设备状态更新设备
    _update_device_status_on_return(
        db,
        reservation.device_id,
        payload.device_condition,
    )
    
    db.commit()
    db.refresh(reservation)
    
    return ok(
        ReservationDetail.model_validate(reservation).model_dump(),
        message=f"归还登记成功，设备状态：{payload.device_condition}"
    )


@router.get("/ledger/summary", response_model=dict)
def get_reservation_ledger_summary(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """
    获取预约台账统计摘要（管理员/负责人）。

    用于仪表盘展示：
    - 按状态统计
    - 按支付状态统计
    - 总记录数
    """
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
