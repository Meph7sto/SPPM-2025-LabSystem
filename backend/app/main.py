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
    将 Pydantic 默认的验证错误结构转换为对前端更友好的格式。

    Args:
        exc (RequestValidationError): Pydantic 抛出的验证异常。

    Returns:
        list[dict[str, str]]: 格式化后的错误列表，每个元素包含 field 和 message。
    """
    details: list[dict[str, str]] = []
    for err in exc.errors():
        # 获取错误发生的字段路径，排除 'body' 这一层级
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

# 解析 CORS 允许的源 (从配置中读取并分割)
allowed_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

# 添加 CORS 中间件，解决跨域访问问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"], # 允许所有 HTTP 方法
    allow_headers=["*"], # 允许所有 Header
)

# 注册 API 路由 (V1版本)
app.include_router(v1_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, object]:
    """
    根路径接口。
    用于简单的服务存活检查 (Ping)。
    """
    return ok({"service": settings.app_name})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    全局异常处理器：处理自定义的业务异常 (AppError)。

    将业务逻辑中抛出的 AppError 转换为统一格式的 JSON 响应。
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
    全局异常处理器：处理请求参数验证异常 (RequestValidationError)。

    当前端传递的参数不符合 Pydantic 模型定义时触发。
    返回 422 Unprocessable Entity 状态码。
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
    全局异常处理器：处理标准 HTTP 异常。

    例如 404 Not Found (路径不存在), 405 Method Not Allowed 等。
    将它们转换为统一的 JSON 错误响应结构。
    """
    code_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
    }
    # 默认为 INTERNAL_ERROR，除非在映射表中找到对应
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
    全局异常处理器：处理所有未捕获的异常 (兜底)。

    通常是代码 bug 或未预料到的系统错误。
    返回 500 Internal Server Error，并隐藏具体错误堆栈以保证安全。
    """
    # 在实际生产环境中，这里应该记录错误日志 (logging.error)
    return JSONResponse(
        status_code=500,
        content=error(ErrorCode.INTERNAL_ERROR, "Internal server error"),
    )
