from fastapi import APIRouter

from ...core.response import ok

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, object]:
    """
    健康检查接口。
    用于负载均衡器或监控系统检查服务是否运行正常。
    """
    return ok({"status": "ok"})
