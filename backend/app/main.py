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


app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
)

allowed_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict[str, object]:
    return ok({"service": settings.app_name})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error(exc.code, exc.message, exc.details),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
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
    return JSONResponse(
        status_code=500,
        content=error(ErrorCode.INTERNAL_ERROR, "Internal server error"),
    )
