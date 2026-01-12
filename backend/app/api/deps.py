from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt

from ..core.security import decode_access_token
from ..db.session import get_db
from ..models.user import BorrowerType, User, UserRole

# 定义 HTTP Bearer 认证方案，用于 Swagger UI 和请求解析
_auth_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_auth_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录用户的依赖项。

    验证 HTTP Authorization 头中的 Bearer Token。
    1. 解析 JWT Token。
    2. 验证 Token 有效性（签名、过期）。
    3. 从 Token 中获取 User ID。
    4. 从数据库查询用户是否存在且处于激活状态。

    Args:
        credentials (HTTPAuthorizationCredentials): Authorization 头信息。
        db (Session): 数据库会话。

    Returns:
        User: 当前登录的用户对象。

    Raises:
        HTTPException: 401 Unauthorized，如果 Token 无效或用户不存在/已禁用。
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    # 获取 Subject (用户ID)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # 查询用户
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

    创建一个依赖项，用于检查当前用户是否具有指定的角色之一。
    常用于保护管理接口。

    Args:
        *roles (UserRole): 允许访问的角色列表。

    Returns:
        Callable: FastAPI 依赖项函数。
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

    创建一个依赖项，用于检查当前借阅者是否具有指定的类型之一。
    常用于区分教师、学生和校外人员的特定接口。

    Args:
        *types (BorrowerType): 允许访问的借阅者类型列表。

    Returns:
        Callable: FastAPI 依赖项函数。
    """
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.borrower_type not in types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return user

    return dependency
