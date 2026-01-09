from typing import Any

from pydantic import BaseModel

from .errors import ErrorCode


class ApiResponse(BaseModel):
    """
    标准 API 响应模型。
    所有 API 接口（除文件下载等特殊接口外）都应返回此结构的 JSON 数据。
    """
    code: str  # 业务状态码，对应 ErrorCode 的值
    message: str  # 提示消息
    data: Any | None = None  # 业务数据载荷
    details: list[dict[str, Any]] | None = None  # 详细错误信息（通常用于验证错误）


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    """
    构建成功响应的辅助函数。

    Args:
        data (Any, optional): 响应数据. 默认为 None.
        message (str, optional): 成功提示消息. 默认为 "ok".

    Returns:
        dict: 符合标准响应结构的字典
    """
    return {"code": ErrorCode.OK.value, "message": message, "data": data}


def error(
    code: ErrorCode,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    构建错误响应的辅助函数。

    Args:
        code (ErrorCode): 错误代码.
        message (str): 错误提示消息.
        details (list[dict], optional): 详细错误列表.

    Returns:
        dict: 符合标准响应结构的字典
    """
    payload: dict[str, Any] = {
        "code": code.value,
        "message": message,
        "data": None,
    }
    if details:
        payload["details"] = details
    return payload
