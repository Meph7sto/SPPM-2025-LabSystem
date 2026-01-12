from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy 声明性基类 (Declarative Base)。

    所有数据库模型 (Model) 都应继承此类。
    DeclarativeBase 是 SQLAlchemy 2.0 推荐的定义模型的方式，
    它自动维护一个 metadata 集合，用于记录所有的表结构信息。
    """
    pass


# 导入所有模型以确保它们在 Base.metadata 中注册
# 这一步对于 Alembic 自动生成迁移脚本至关重要，
# 如果不导入，Alembic 无法检测到模型定义。
from ..models import user, device, reservation  # noqa: E402,F401
