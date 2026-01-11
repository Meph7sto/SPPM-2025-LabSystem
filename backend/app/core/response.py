from typing import Any

from pydantic import BaseModel

from .errors import ErrorCode


class ApiResponse(BaseModel):
    """
    标准 API 响应模型。
    """
    code: str
    message: str
    data: Any | None = None
    details: list[dict[str, Any]] | None = None


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    """
    构建成功响应的辅助函数。
    """
    return {"code": ErrorCode.OK.value, "message": message, "data": data}


def error(
    code: ErrorCode,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    构建错误响应的辅助函数。
    """
    payload: dict[str, Any] = {
        "code": code.value,
        "message": message,
        "data": None,
    }
    if details:
        payload["details"] = details
    return payload
