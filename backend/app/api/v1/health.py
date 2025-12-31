from fastapi import APIRouter

from ...core.response import ok

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, object]:
    return ok({"status": "ok"})
