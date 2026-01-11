from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """
    应用层错误代码枚举。
    """
    OK = "OK"  # 成功
    BAD_REQUEST = "BAD_REQUEST"  # 错误的请求
    INVALID_REQUEST = "INVALID_REQUEST"  # 无效请求
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 数据验证错误
    UNAUTHORIZED = "UNAUTHORIZED"  # 未授权
    FORBIDDEN = "FORBIDDEN"  # 禁止访问
    PERMISSION_DENIED = "PERMISSION_DENIED"  # 权限不足
    NOT_FOUND = "NOT_FOUND"  # 资源不存在
    CONFLICT = "CONFLICT"  # 资源冲突
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 内部错误


class AppError(Exception):
    """
    应用层基础异常类。
    """
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    """
    资源未找到异常。
    """
    def __init__(
        self,
        message: str = "Resource not found",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=message,
            status_code=404,
            details=details,
        )
