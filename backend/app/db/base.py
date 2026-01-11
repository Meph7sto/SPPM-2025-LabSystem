from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy 声明性基类。
    所有模型都应继承此类。
    """
    pass


# 导入所有模型以确保它们在 Base.metadata 中注册
from ..models import user, device, reservation  # noqa: E402,F401
