from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt

from ..core.security import decode_access_token
from ..db.session import get_db
from ..models.user import BorrowerType, User, UserRole

_auth_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_auth_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录用户的依赖项。
    验证 JWT 令牌并检索用户信息。
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = db.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return user


def require_roles(*roles: UserRole):
    """
    基于角色的访问控制依赖项工厂。
    创建一个检查用户是否具有指定角色之一的依赖项。
    """
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return user

    return dependency


def require_borrower_types(*types: BorrowerType):
    """
    基于借阅者类型的访问控制依赖项工厂。
    创建一个检查用户是否具有指定借阅者类型之一的依赖项。
    """
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.borrower_type not in types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return user

    return dependency
