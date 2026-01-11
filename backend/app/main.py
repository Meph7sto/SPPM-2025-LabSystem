from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.v1.router import router as v1_router
from .core.config import settings
from .core.errors import AppError, ErrorCode
from .core.response import error, ok


def format_validation_errors(
    exc: RequestValidationError,
) -> list[dict[str, str]]:
    """
    格式化请求验证错误信息。
    将 Pydantic 验证错误转换为更友好的格式。
    """
    details: list[dict[str, str]] = []
    for err in exc.errors():
        raw_loc = [str(item) for item in err.get("loc", [])]
        loc = ".".join([item for item in raw_loc if item != "body"])
        details.append(
            {
                "field": loc or "body",
                "message": err.get("msg", "Invalid value"),
            }
        )
    return details


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
)

# 解析 CORS 允许的源
allowed_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(v1_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, object]:
    """根路径，用于检查服务是否运行"""
    return ok({"service": settings.app_name})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    统一处理自定义 AppError 异常。
    返回规范的 JSON 错误响应。
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=error(exc.code, exc.message, exc.details),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    处理请求参数验证错误。
    """
    details = format_validation_errors(exc)
    return JSONResponse(
        status_code=422,
        content=error(ErrorCode.VALIDATION_ERROR, "Validation failed", details),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """
    处理标准 HTTP 异常。
    将其映射到应用错误代码。
    """
    code_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
    }
    code = code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content=error(code, message),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    处理所有未捕获的异常（500 错误）。
    """
    return JSONResponse(
        status_code=500,
        content=error(ErrorCode.INTERNAL_ERROR, "Internal server error"),
    )
