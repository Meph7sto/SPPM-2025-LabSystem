from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.errors import AppError, ErrorCode
from ...core.response import ok
from ...core.security import create_access_token, hash_password, verify_password
from ...db.session import get_db
from ...models.user import BorrowerType, User, UserRole
from ...schemas.auth import LoginRequest, LoginRole, RegisterRequest, TokenResponse, UserOut
from ..deps import get_current_user

router = APIRouter(prefix="/auth")


def build_account(payload: RegisterRequest) -> str:
    """
    根据角色类型生成系统内部账号标识。

    - 教师：使用工号。
    - 学生：使用学号。
    - 校外人员：使用联系方式（手机号）。
    此逻辑确保了账号的唯一性和业务含义。
    """
    if payload.role == BorrowerType.TEACHER:
        return payload.teacher_no or ""
    if payload.role == BorrowerType.STUDENT:
        return payload.student_no or ""
    return payload.contact


def to_user_out(user: User) -> UserOut:
    """将 User 模型转换为 UserOut Schema"""
    return UserOut.model_validate(user)


@router.post("/register", response_model=dict)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    """
    用户注册接口。

    支持教师、学生、校外人员注册。
    注册成功后，账号默认为激活状态 (is_active=True)，可直接登录。
    """
    # 1. 生成账号
    account = build_account(payload)
    if not account:
        raise AppError(
            ErrorCode.BAD_REQUEST,
            "Account identifier is missing",
        )

    # 2. 检查账号是否存在
    existing = db.scalar(select(User).where(User.account == account))
    if existing:
        raise AppError(
            ErrorCode.CONFLICT,
            "Account already exists",
            status_code=409,
        )

    # 3. 创建用户
    user = User(
        account=account,
        password_hash=hash_password(payload.password), # 密码加密
        role=UserRole.BORROWER, # 注册用户默认为借阅者角色
        borrower_type=payload.role,
        name=payload.name,
        contact=payload.contact,
        college=payload.college,
        teacher_no=payload.teacher_no,
        student_no=payload.student_no,
        advisor_no=payload.advisor_no,
        org_name=payload.org_name,
        is_active=True,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        # 处理可能的并发冲突
        raise AppError(
            ErrorCode.CONFLICT,
            "Account already exists",
            status_code=409,
        ) from exc

    db.refresh(user)
    return ok(to_user_out(user).model_dump())


@router.post("/login", response_model=dict)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    """
    用户登录接口。

    验证账号密码，验证通过后颁发 JWT Access Token。
    同时会校验前端选择的登录角色与后端记录是否一致。
    """
    # 1. 查找用户
    user = db.scalar(select(User).where(User.account == payload.account))

    # 2. 验证密码
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppError(
            ErrorCode.UNAUTHORIZED,
            "Invalid credentials",
            status_code=401,
        )

    # 3. 检查账号状态
    if not user.is_active:
        raise AppError(
            ErrorCode.UNAUTHORIZED,
            "Inactive account",
            status_code=401,
        )

    # 4. 验证角色匹配 (防止用户选错入口或恶意尝试)
    if payload.role in (LoginRole.ADMIN, LoginRole.HEAD):
        required_role = UserRole.ADMIN if payload.role == LoginRole.ADMIN else UserRole.HEAD
        if user.role != required_role:
            raise AppError(
                ErrorCode.FORBIDDEN,
                "Role mismatch",
                status_code=403,
            )
    else:
        # 验证借阅者类型
        expected_type = BorrowerType(payload.role.value)
        if user.role != UserRole.BORROWER or user.borrower_type != expected_type:
            raise AppError(
                ErrorCode.FORBIDDEN,
                "Role mismatch",
                status_code=403,
            )

    # 5. 生成 Token
    token = create_access_token(
        subject=str(user.id),
        role=user.role.value,
        borrower_type=user.borrower_type.value if user.borrower_type else None,
        expires_minutes=settings.jwt_expire_minutes,
    )

    data = TokenResponse(
        access_token=token,
        token_type="bearer",
        user=to_user_out(user),
    )
    return ok(data.model_dump())


@router.get("/me", response_model=dict)
def me(current_user: User = Depends(get_current_user)) -> dict:
    """
    获取当前登录用户信息接口。

    需要有效的 JWT Token。通常用于前端页面刷新后恢复用户状态。
    """
    return ok(to_user_out(current_user).model_dump())
