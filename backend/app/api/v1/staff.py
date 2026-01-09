from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ...core.errors import AppError, ErrorCode, NotFoundError
from ...core.response import ok
from ...core.security import get_password_hash
from ...db.session import get_db
from ...models.user import User, UserRole, BorrowerType
from ...schemas.staff import (
    TeacherCreate, TeacherUpdate, TeacherOut,
    StudentCreate, StudentUpdate, StudentOut,
    ExternalCreate, ExternalUpdate, ExternalOut,
)
from ..deps import require_roles

router = APIRouter(prefix="/staff")


# ==================== 教师台账 CRUD ====================

@router.post("/teachers", response_model=dict)
def create_teacher(
    payload: TeacherCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """创建教师台账记录（管理员/负责人）"""
    # 检查工号唯一性
    stmt = select(User).where(User.teacher_no == payload.teacher_no)
    if db.execute(stmt).scalar_one_or_none():
        raise AppError(ErrorCode.INVALID_REQUEST, "教师工号已存在")
    
    # 使用工号作为账号
    account = f"T{payload.teacher_no}"
    stmt = select(User).where(User.account == account)
    if db.execute(stmt).scalar_one_or_none():
        raise AppError(ErrorCode.INVALID_REQUEST, "账号已存在")
    
    teacher = User(
        account=account,
        password_hash=get_password_hash(payload.password),
        role=UserRole.BORROWER,
        borrower_type=BorrowerType.TEACHER,
        name=payload.name,
        contact=payload.contact,
        college=payload.college,
        teacher_no=payload.teacher_no,
        is_active=True,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return ok(TeacherOut.model_validate(teacher).model_dump(), message="教师创建成功")


@router.get("/teachers", response_model=dict)
def list_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str = Query(None, description="搜索关键词（姓名/工号）"),
    college: str = Query(None, description="按学院筛选"),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取教师台账列表（管理员/负责人）"""
    stmt = select(User).where(
        User.role == UserRole.BORROWER,
        User.borrower_type == BorrowerType.TEACHER
    )
    
    if keyword:
        stmt = stmt.where(
            (User.name.ilike(f"%{keyword}%")) | 
            (User.teacher_no.ilike(f"%{keyword}%"))
        )
    if college:
        stmt = stmt.where(User.college.ilike(f"%{college}%"))
    
    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # 分页
    stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
    teachers = db.execute(stmt).scalars().all()
    
    return ok({
        "items": [TeacherOut.model_validate(t).model_dump() for t in teachers],
        "total": total,
        "skip": skip,
        "limit": limit,
    })


@router.get("/teachers/{teacher_id}", response_model=dict)
def get_teacher(
    teacher_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取教师详情（管理员/负责人）"""
    teacher = db.get(User, teacher_id)
    if not teacher or teacher.borrower_type != BorrowerType.TEACHER:
        raise NotFoundError("教师不存在")
    return ok(TeacherOut.model_validate(teacher).model_dump())


@router.put("/teachers/{teacher_id}", response_model=dict)
def update_teacher(
    teacher_id: int,
    payload: TeacherUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """更新教师台账（管理员/负责人）"""
    teacher = db.get(User, teacher_id)
    if not teacher or teacher.borrower_type != BorrowerType.TEACHER:
        raise NotFoundError("教师不存在")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(teacher, key, value)
    
    db.commit()
    db.refresh(teacher)
    return ok(TeacherOut.model_validate(teacher).model_dump(), message="教师更新成功")


@router.delete("/teachers/{teacher_id}", response_model=dict)
def delete_teacher(
    teacher_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """删除教师台账（管理员/负责人）"""
    teacher = db.get(User, teacher_id)
    if not teacher or teacher.borrower_type != BorrowerType.TEACHER:
        raise NotFoundError("教师不存在")
    
    db.delete(teacher)
    db.commit()
    return ok({"id": teacher_id}, message="教师删除成功")


# ==================== 学生台账 CRUD ====================

@router.post("/students", response_model=dict)
def create_student(
    payload: StudentCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """创建学生台账记录（管理员/负责人）"""
    # 检查学号唯一性
    stmt = select(User).where(User.student_no == payload.student_no)
    if db.execute(stmt).scalar_one_or_none():
        raise AppError(ErrorCode.INVALID_REQUEST, "学号已存在")
    
    # 验证导师是否存在
    stmt = select(User).where(User.teacher_no == payload.advisor_no)
    if not db.execute(stmt).scalar_one_or_none():
        raise AppError(ErrorCode.INVALID_REQUEST, "导师工号不存在")
    
    # 使用学号作为账号
    account = f"S{payload.student_no}"
    stmt = select(User).where(User.account == account)
    if db.execute(stmt).scalar_one_or_none():
        raise AppError(ErrorCode.INVALID_REQUEST, "账号已存在")
    
    student = User(
        account=account,
        password_hash=get_password_hash(payload.password),
        role=UserRole.BORROWER,
        borrower_type=BorrowerType.STUDENT,
        name=payload.name,
        contact=payload.contact,
        college=payload.college,
        student_no=payload.student_no,
        advisor_no=payload.advisor_no,
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return ok(StudentOut.model_validate(student).model_dump(), message="学生创建成功")


@router.get("/students", response_model=dict)
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str = Query(None, description="搜索关键词（姓名/学号）"),
    college: str = Query(None, description="按学院筛选"),
    advisor_no: str = Query(None, description="按导师工号筛选"),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取学生台账列表（管理员/负责人）"""
    stmt = select(User).where(
        User.role == UserRole.BORROWER,
        User.borrower_type == BorrowerType.STUDENT
    )
    
    if keyword:
        stmt = stmt.where(
            (User.name.ilike(f"%{keyword}%")) | 
            (User.student_no.ilike(f"%{keyword}%"))
        )
    if college:
        stmt = stmt.where(User.college.ilike(f"%{college}%"))
    if advisor_no:
        stmt = stmt.where(User.advisor_no == advisor_no)
    
    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # 分页
    stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
    students = db.execute(stmt).scalars().all()
    
    return ok({
        "items": [StudentOut.model_validate(s).model_dump() for s in students],
        "total": total,
        "skip": skip,
        "limit": limit,
    })


@router.get("/students/{student_id}", response_model=dict)
def get_student(
    student_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取学生详情（管理员/负责人）"""
    student = db.get(User, student_id)
    if not student or student.borrower_type != BorrowerType.STUDENT:
        raise NotFoundError("学生不存在")
    return ok(StudentOut.model_validate(student).model_dump())


@router.put("/students/{student_id}", response_model=dict)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """更新学生台账（管理员/负责人）"""
    student = db.get(User, student_id)
    if not student or student.borrower_type != BorrowerType.STUDENT:
        raise NotFoundError("学生不存在")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    # 如果更新导师，验证导师存在
    if "advisor_no" in update_data and update_data["advisor_no"]:
        stmt = select(User).where(User.teacher_no == update_data["advisor_no"])
        if not db.execute(stmt).scalar_one_or_none():
            raise AppError(ErrorCode.INVALID_REQUEST, "导师工号不存在")
    
    for key, value in update_data.items():
        setattr(student, key, value)
    
    db.commit()
    db.refresh(student)
    return ok(StudentOut.model_validate(student).model_dump(), message="学生更新成功")


@router.delete("/students/{student_id}", response_model=dict)
def delete_student(
    student_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """删除学生台账（管理员/负责人）"""
    student = db.get(User, student_id)
    if not student or student.borrower_type != BorrowerType.STUDENT:
        raise NotFoundError("学生不存在")
    
    db.delete(student)
    db.commit()
    return ok({"id": student_id}, message="学生删除成功")


# ==================== 校外人员台账 CRUD ====================

@router.post("/externals", response_model=dict)
def create_external(
    payload: ExternalCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """创建校外人员台账记录（管理员/负责人）"""
    # 使用联系方式作为账号（校外人员没有工号/学号）
    account = f"E{payload.contact}"
    stmt = select(User).where(User.account == account)
    if db.execute(stmt).scalar_one_or_none():
        raise AppError(ErrorCode.INVALID_REQUEST, "账号已存在")
    
    external = User(
        account=account,
        password_hash=get_password_hash(payload.password),
        role=UserRole.BORROWER,
        borrower_type=BorrowerType.EXTERNAL,
        name=payload.name,
        contact=payload.contact,
        org_name=payload.org_name,
        is_active=True,
    )
    db.add(external)
    db.commit()
    db.refresh(external)
    return ok(ExternalOut.model_validate(external).model_dump(), message="校外人员创建成功")


@router.get("/externals", response_model=dict)
def list_externals(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    keyword: str = Query(None, description="搜索关键词（姓名/单位）"),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取校外人员台账列表（管理员/负责人）"""
    stmt = select(User).where(
        User.role == UserRole.BORROWER,
        User.borrower_type == BorrowerType.EXTERNAL
    )
    
    if keyword:
        stmt = stmt.where(
            (User.name.ilike(f"%{keyword}%")) | 
            (User.org_name.ilike(f"%{keyword}%"))
        )
    
    # 获取总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # 分页
    stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
    externals = db.execute(stmt).scalars().all()
    
    return ok({
        "items": [ExternalOut.model_validate(e).model_dump() for e in externals],
        "total": total,
        "skip": skip,
        "limit": limit,
    })


@router.get("/externals/{external_id}", response_model=dict)
def get_external(
    external_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取校外人员详情（管理员/负责人）"""
    external = db.get(User, external_id)
    if not external or external.borrower_type != BorrowerType.EXTERNAL:
        raise NotFoundError("校外人员不存在")
    return ok(ExternalOut.model_validate(external).model_dump())


@router.put("/externals/{external_id}", response_model=dict)
def update_external(
    external_id: int,
    payload: ExternalUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """更新校外人员台账（管理员/负责人）"""
    external = db.get(User, external_id)
    if not external or external.borrower_type != BorrowerType.EXTERNAL:
        raise NotFoundError("校外人员不存在")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(external, key, value)
    
    db.commit()
    db.refresh(external)
    return ok(ExternalOut.model_validate(external).model_dump(), message="校外人员更新成功")


@router.delete("/externals/{external_id}", response_model=dict)
def delete_external(
    external_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """删除校外人员台账（管理员/负责人）"""
    external = db.get(User, external_id)
    if not external or external.borrower_type != BorrowerType.EXTERNAL:
        raise NotFoundError("校外人员不存在")
    
    db.delete(external)
    db.commit()
    return ok({"id": external_id}, message="校外人员删除成功")


# ==================== 统计接口 ====================

@router.get("/stats", response_model=dict)
def get_staff_stats(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """获取人员台账统计（管理员/负责人）"""
    teacher_count = db.execute(
        select(func.count()).where(
            User.role == UserRole.BORROWER,
            User.borrower_type == BorrowerType.TEACHER
        )
    ).scalar() or 0
    
    student_count = db.execute(
        select(func.count()).where(
            User.role == UserRole.BORROWER,
            User.borrower_type == BorrowerType.STUDENT
        )
    ).scalar() or 0
    
    external_count = db.execute(
        select(func.count()).where(
            User.role == UserRole.BORROWER,
            User.borrower_type == BorrowerType.EXTERNAL
        )
    ).scalar() or 0
    
    return ok({
        "teachers": teacher_count,
        "students": student_count,
        "externals": external_count,
        "total": teacher_count + student_count + external_count,
    })
