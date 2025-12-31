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
    if payload.role == BorrowerType.TEACHER:
        return payload.teacher_no or ""
    if payload.role == BorrowerType.STUDENT:
        return payload.student_no or ""
    return payload.contact


def to_user_out(user: User) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/register", response_model=dict)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    account = build_account(payload)
    if not account:
        raise AppError(
            ErrorCode.BAD_REQUEST,
            "Account identifier is missing",
        )
    existing = db.scalar(select(User).where(User.account == account))
    if existing:
        raise AppError(
            ErrorCode.CONFLICT,
            "Account already exists",
            status_code=409,
        )
    user = User(
        account=account,
        password_hash=hash_password(payload.password),
        role=UserRole.BORROWER,
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
        raise AppError(
            ErrorCode.CONFLICT,
            "Account already exists",
            status_code=409,
        ) from exc
    db.refresh(user)
    return ok(to_user_out(user).model_dump())


@router.post("/login", response_model=dict)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(select(User).where(User.account == payload.account))
    if not user or not verify_password(payload.password, user.password_hash):
        raise AppError(
            ErrorCode.UNAUTHORIZED,
            "Invalid credentials",
            status_code=401,
        )
    if not user.is_active:
        raise AppError(
            ErrorCode.UNAUTHORIZED,
            "Inactive account",
            status_code=401,
        )
    if payload.role in (LoginRole.ADMIN, LoginRole.HEAD):
        required_role = UserRole.ADMIN if payload.role == LoginRole.ADMIN else UserRole.HEAD
        if user.role != required_role:
            raise AppError(
                ErrorCode.FORBIDDEN,
                "Role mismatch",
                status_code=403,
            )
    else:
        expected_type = BorrowerType(payload.role.value)
        if user.role != UserRole.BORROWER or user.borrower_type != expected_type:
            raise AppError(
                ErrorCode.FORBIDDEN,
                "Role mismatch",
                status_code=403,
            )
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
    return ok(to_user_out(current_user).model_dump())
