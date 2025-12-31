from fastapi import APIRouter

from .auth import router as auth_router
from .health import router as health_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(auth_router, tags=["auth"])
