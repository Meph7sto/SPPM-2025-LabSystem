from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from ...core.errors import AppError, ErrorCode, NotFoundError
from ...core.response import ok
from ...db.session import get_db
from ...models.reservation import Reservation, ReservationStatus, PaymentStatus, ApprovalStep
from ...models.user import User, UserRole, BorrowerType
from ...schemas import ReservationCreate, ReservationDetail, ReservationUpdate, ReservationListItem
from ..deps import get_current_user, require_roles

router = APIRouter(prefix="/reservations")


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
