from typing import Any

from pydantic import BaseModel

from .errors import ErrorCode


class ApiResponse(BaseModel):
    code: str
    message: str
    data: Any | None = None
    details: list[dict[str, Any]] | None = None


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    return {"code": ErrorCode.OK.value, "message": message, "data": data}


def error(
    code: ErrorCode,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code.value,
        "message": message,
        "data": None,
    }
    if details:
        payload["details"] = details
    return payload
