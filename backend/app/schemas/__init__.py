from .auth import LoginRequest, LoginRole, RegisterRequest, TokenResponse, UserOut

__all__ = [
    "LoginRequest",
    "LoginRole",
    "RegisterRequest",
    "TokenResponse",
    "UserOut",
    "DeviceOut",
    "DeviceCreate",
    "DeviceUpdate",
    "ReservationOut",
    "ReservationCreate",
    "ReservationUpdate",
    "ReservationDetail",
    "ReservationListItem",
    "ApprovalAction",
    # Staff schemas
    "TeacherCreate",
    "TeacherUpdate",
    "TeacherOut",
    "StudentCreate",
    "StudentUpdate",
    "StudentOut",
    "ExternalCreate",
    "ExternalUpdate",
    "ExternalOut",
]

from .device import DeviceCreate, DeviceOut, DeviceUpdate
from .reservation import (
    ApprovalAction,
    ReservationCreate,
    ReservationDetail,
    ReservationListItem,
    ReservationOut,
    ReservationUpdate,
)
from .staff import (
    TeacherCreate,
    TeacherUpdate,
    TeacherOut,
    StudentCreate,
    StudentUpdate,
    StudentOut,
    ExternalCreate,
    ExternalUpdate,
    ExternalOut,
)
