"""
API v1 路由注册
此文件用于导入和注册所有 v1 版本的路由
"""

from fastapi import APIRouter

# 导入各个模块
from . import auth
from . import users
from . import devices
from . import maintenance_windows
from . import reservations
from . import reports
from . import system_config  # 系统配置接口
from . import staff
from . import finance
from . import health

# 创建主路由
router = APIRouter()

# 注册各个子路由
router.include_router(auth.router, tags=["Auth"])
router.include_router(users.router, tags=["Users"])
router.include_router(devices.router, tags=["Devices"])
router.include_router(maintenance_windows.router, tags=["Maintenance Windows"])
router.include_router(reservations.router, tags=["Reservations"])
router.include_router(reports.router, tags=["Reports"])
router.include_router(system_config.router, tags=["System Config"])  # 你的接口
router.include_router(staff.router, tags=["Staff"])
router.include_router(finance.router, tags=["Finance"])
router.include_router(health.router, tags=["Health"])

# 你可以通过 __all__ 控制导出的内容
__all__ = [
    "auth",
    "users",
    "devices",
    "maintenance_windows",
    "reservations",
    "reports",
    "system_config",
    "staff",
    "finance",
    "health",
    "router",  # 导出主路由对象
]
