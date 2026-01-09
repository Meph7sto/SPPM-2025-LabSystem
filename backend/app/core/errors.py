from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """
    应用层错误代码枚举。
    定义了系统中所有可预见的业务错误类型，用于统一前端错误处理逻辑。
    """
    OK = "OK"  # 操作成功
    BAD_REQUEST = "BAD_REQUEST"  # 请求参数格式错误或缺失
    INVALID_REQUEST = "INVALID_REQUEST"  # 请求参数逻辑无效（如日期格式不对，结束时间早于开始时间）
    VALIDATION_ERROR = "VALIDATION_ERROR"  # Pydantic 数据模型验证失败
    UNAUTHORIZED = "UNAUTHORIZED"  # 用户未登录或 Token 无效/过期
    FORBIDDEN = "FORBIDDEN"  # 用户已登录但无权限执行该操作（如学生尝试审批）
    PERMISSION_DENIED = "PERMISSION_DENIED"  # 具体的权限拒绝（如尝试查看他人的私有数据）
    NOT_FOUND = "NOT_FOUND"  # 请求的资源（用户、设备、预约等）不存在
    CONFLICT = "CONFLICT"  # 资源状态冲突（如账号已存在、设备已被占用）
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 服务器内部未知错误


class AppError(Exception):
    """
    应用层基础异常类。
    所有业务逻辑中抛出的异常都应继承此类或直接使用此类。
    FastAPI 的异常处理器会捕获此类异常并转换为标准 JSON 响应。
    """
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        初始化应用异常。

        Args:
            code (ErrorCode): 错误代码枚举值。
            message (str): 错误描述信息，可直接展示给用户。
            status_code (int): 对应的 HTTP 状态码，默认为 400 Bad Request。
            details (list[dict], optional): 详细的错误信息列表，通常用于表单验证错误。
        """
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    """
    资源未找到异常 (404)。
    AppError 的便捷子类，用于快速抛出 404 错误。
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
