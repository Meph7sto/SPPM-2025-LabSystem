from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, File, UploadFile

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
from ..deps import require_roles, get_current_user


router = APIRouter(prefix="/staff")

"""
人员台账管理模块。
提供教师、学生、校外人员的 CRUD 接口。
主要供管理员和负责人使用。
"""

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
    
    # 生成账号：T + 工号
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
        gender=payload.gender,
        college=payload.college,
        professional_title=payload.professional_title,
        research_direction=payload.research_direction,
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
    """获取教师台账列表"""
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
    
    # 总数
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
    """获取教师详情"""
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
    """更新教师信息"""
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
    """删除教师"""
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """创建 student 台账记录（管理员/负责人/导师）"""
    # 权限检查
    is_management = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_teacher = (current_user.role == UserRole.BORROWER and current_user.borrower_type == BorrowerType.TEACHER)
    
    if not (is_management or is_teacher):
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权创建学生记录")

    # 如果是导师，强制设为自己的学生
    advisor_no = payload.advisor_no
    if is_teacher:
        advisor_no = current_user.teacher_no

    # 检查学号唯一性
    stmt = select(User).where(User.student_no == payload.student_no)
    if db.execute(stmt).scalar_one_or_none():
        raise AppError(ErrorCode.INVALID_REQUEST, "学号已存在")
    
    # 验证导师是否存在
    stmt = select(User).where(User.teacher_no == advisor_no)
    if not db.execute(stmt).scalar_one_or_none():
        raise AppError(ErrorCode.INVALID_REQUEST, f"导师工号 {advisor_no} 不存在")
    
    # 生成账号：S + 学号
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
        gender=payload.gender,
        college=payload.college,
        student_no=payload.student_no,
        major=payload.major,
        advisor_no=advisor_no,
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取学生台账列表（管理员/负责人/导师）"""
    is_management = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_teacher = (current_user.role == UserRole.BORROWER and current_user.borrower_type == BorrowerType.TEACHER)
    
    if not (is_management or is_teacher):
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权查看学生列表")

    stmt = select(User).where(
        User.role == UserRole.BORROWER,
        User.borrower_type == BorrowerType.STUDENT
    )
    
    # 导师只能看自己的学生
    if is_teacher:
        stmt = stmt.where(User.advisor_no == current_user.teacher_no)
    elif advisor_no:
        stmt = stmt.where(User.advisor_no == advisor_no)
    
    if keyword:
        stmt = stmt.where(
            (User.name.ilike(f"%{keyword}%")) | 
            (User.student_no.ilike(f"%{keyword}%"))
        )
    if college:
        stmt = stmt.where(User.college.ilike(f"%{college}%"))
    
    # 总数
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """获取学生详情"""
    student = db.get(User, student_id)
    if not student or student.borrower_type != BorrowerType.STUDENT:
        raise NotFoundError("学生不存在")
        
    is_management = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_teacher = (current_user.role == UserRole.BORROWER and current_user.borrower_type == BorrowerType.TEACHER)
    
    if is_teacher and student.advisor_no != current_user.teacher_no:
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权查看非指导学生详情")
    if not (is_management or is_teacher):
        raise AppError(ErrorCode.PERMISSION_DENIED, "访问受限")

    return ok(StudentOut.model_validate(student).model_dump())


@router.put("/students/{student_id}", response_model=dict)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """更新学生信息"""
    student = db.get(User, student_id)
    if not student or student.borrower_type != BorrowerType.STUDENT:
        raise NotFoundError("学生不存在")
        
    is_management = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_teacher = (current_user.role == UserRole.BORROWER and current_user.borrower_type == BorrowerType.TEACHER)
    
    if is_teacher and student.advisor_no != current_user.teacher_no:
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权更新非指导学生")
    if not (is_management or is_teacher):
        raise AppError(ErrorCode.PERMISSION_DENIED, "访问受限")

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """删除学生"""
    student = db.get(User, student_id)
    if not student or student.borrower_type != BorrowerType.STUDENT:
        raise NotFoundError("学生不存在")
        
    is_management = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_teacher = (current_user.role == UserRole.BORROWER and current_user.borrower_type == BorrowerType.TEACHER)
    
    if is_teacher and student.advisor_no != current_user.teacher_no:
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权删除非指导学生")
    if not (is_management or is_teacher):
        raise AppError(ErrorCode.PERMISSION_DENIED, "访问受限")

    db.delete(student)
    db.commit()
    return ok({"id": student_id}, message="学生删除成功")


@router.post("/students/import", response_model=dict)
async def import_students(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Excel/CSV 批量导入指导学生名单（FR-29）。
    支持教师导入（自动关联自己）或管理员导入（需指定导师工号）。
    """
    is_management = current_user.role in [UserRole.ADMIN, UserRole.HEAD]
    is_teacher = (current_user.role == UserRole.BORROWER and current_user.borrower_type == BorrowerType.TEACHER)
    
    if not (is_management or is_teacher):
        raise AppError(ErrorCode.PERMISSION_DENIED, "无权导入学生名单")

    content = await file.read()
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        text_content = content.decode("gbk")  # 兼容 Excel 导出的 CSV

    import csv
    import io
    
    reader = csv.DictReader(io.StringIO(text_content))
    success_count = 0
    fail_details = []

    for row in reader:
        try:
            s_no = row.get("studentNo") or row.get("学号")
            name = row.get("name") or row.get("姓名")
            
            if not s_no or not name:
                raise ValueError("学号和姓名必填")

            # 确定导师工号
            row_advisor_no = row.get("advisorNo") or row.get("导师工号")
            effective_advisor_no = current_user.teacher_no if is_teacher else row_advisor_no
            
            if not effective_advisor_no:
                raise ValueError("未指定导师工号")

            # 校验唯一性
            stmt = select(User).where(User.student_no == s_no)
            if db.execute(stmt).scalar_one_or_none():
                raise ValueError(f"学号 {s_no} 已存在")

            student = User(
                account=f"S{s_no}",
                password_hash=get_password_hash("12345678"), # 默认初始密码
                role=UserRole.BORROWER,
                borrower_type=BorrowerType.STUDENT,
                name=name,
                contact=row.get("contact", "") or row.get("联系方式", ""),
                gender=row.get("gender", "") or row.get("性别", ""),
                college=row.get("college", "") or row.get("学院", ""),
                student_no=s_no,
                major=row.get("major", "") or row.get("专业", ""),
                advisor_no=effective_advisor_no,
                is_active=True,
            )
            db.add(student)
            success_count += 1
        except Exception as e:
            fail_details.append(f"行 {reader.line_num}: {str(e)}")

    db.commit()
    return ok({
        "success": success_count,
        "failed": len(fail_details),
        "errors": fail_details
    }, message=f"导入完成：成功 {success_count} 条，失败 {len(fail_details)} 条")


# ==================== 校外人员台账 CRUD ====================

@router.post("/externals", response_model=dict)
def create_external(
    payload: ExternalCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HEAD)),
    db: Session = Depends(get_db),
) -> dict:
    """创建校外人员台账记录（管理员/负责人）"""
    # 生成账号：E + 联系方式
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
        gender=payload.gender,
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
    """获取校外人员台账列表"""
    stmt = select(User).where(
        User.role == UserRole.BORROWER,
        User.borrower_type == BorrowerType.EXTERNAL
    )
    
    if keyword:
        stmt = stmt.where(
            (User.name.ilike(f"%{keyword}%")) | 
            (User.org_name.ilike(f"%{keyword}%"))
        )
    
    # 总数
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
    """获取校外人员详情"""
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
    """更新校外人员信息"""
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
    """删除校外人员"""
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
    """
    获取人员台账统计数据（管理员/负责人）。
    用于仪表盘展示各类人员数量。
    """
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
