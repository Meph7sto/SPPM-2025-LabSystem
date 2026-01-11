from fastapi import APIRouter

from .auth import router as auth_router
from .health import router as health_router
from .users import router as users_router

from .devices import router as devices_router
from .reservations import router as reservations_router
from .staff import router as staff_router
from .reports import router as reports_router

router = APIRouter()
router.include_router(reports_router, prefix="/reports", tags=["reports"])
router.include_router(health_router, tags=["health"])
router.include_router(auth_router, tags=["auth"])
router.include_router(users_router, tags=["users"])
router.include_router(devices_router, tags=["devices"])
router.include_router(reservations_router, tags=["reservations"])
router.include_router(staff_router, tags=["staff"])

