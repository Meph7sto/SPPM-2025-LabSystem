from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"        # 管理员
    HEAD = "head"          # 实验室/部门负责人
    BORROWER = "borrower"  # 借阅者


class BorrowerType(str, enum.Enum):
    """借阅者类型枚举"""
    TEACHER = "teacher"    # 教师
    STUDENT = "student"    # 学生
    EXTERNAL = "external"  # 校外人员


class User(Base):
    """
    用户模型。
    存储系统用户信息，包括管理员、负责人和借阅者。
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # 账号/用户名
    account: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    # 密码哈希
    password_hash: Mapped[str] = mapped_column(String(256))
    # 用户角色
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.BORROWER,
        nullable=False,
    )
    # 借阅者类型（仅当角色为 borrower 时有值）
    borrower_type: Mapped[BorrowerType | None] = mapped_column(
        Enum(BorrowerType, name="borrower_type", native_enum=False),
        nullable=True,
    )
    # 真实姓名
    name: Mapped[str] = mapped_column(String(64))
    # 联系方式（电话/邮箱）
    contact: Mapped[str] = mapped_column(String(64))
    # 学院/部门
    college: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # 工号（教师）
    teacher_no: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    # 学号（学生）
    student_no: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    # 导师工号（学生）
    advisor_no: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # 单位名称（校外人员）
    org_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # 账号是否启用
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
