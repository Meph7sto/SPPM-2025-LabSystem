from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class UserRole(str, enum.Enum):
    """
    用户系统角色枚举。
    决定用户在系统中的管理权限。
    """
    ADMIN = "admin"        # 系统管理员：拥有最高权限，管理设备、用户和所有预约
    HEAD = "head"          # 实验室/部门负责人：负责审批校外人员申请，查看统计数据
    BORROWER = "borrower"  # 普通借阅者：包括教师、学生和校外人员，只能提交和查看自己的预约


class BorrowerType(str, enum.Enum):
    """
    借阅者身份类型枚举。
    进一步区分 BORROWER 角色的具体身份，决定审批流程。
    """
    TEACHER = "teacher"    # 教师：申请流程相对简单
    STUDENT = "student"    # 学生：申请需要导师审批
    EXTERNAL = "external"  # 校外人员：申请需要负责人审批并涉及付费


class User(Base):
    """
    用户模型。
    对应数据库表 `users`。

    存储系统所有用户的信息，包括管理员、负责人和各类型的借阅者。
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 账号/用户名
    # 唯一标识，根据角色不同可能是工号、学号或手机号前缀
    account: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    # 密码哈希值
    # 存储经过加盐哈希处理的密码字符串
    password_hash: Mapped[str] = mapped_column(String(256))

    # 用户角色 (Admin/Head/Borrower)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.BORROWER,
        nullable=False,
    )

    # 借阅者类型 (Teacher/Student/External)
    # 仅当 role 为 BORROWER 时该字段有意义
    borrower_type: Mapped[BorrowerType | None] = mapped_column(
        Enum(BorrowerType, name="borrower_type", native_enum=False),
        nullable=True,
    )

    # 真实姓名
    name: Mapped[str] = mapped_column(String(64))

    # 联系方式 (电话/邮箱)
    contact: Mapped[str] = mapped_column(String(64))

    # -------------------------------------------------------------------------
    # 身份特定字段
    # -------------------------------------------------------------------------

    # 学院/部门 (教师/学生必填)
    college: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # 教师工号 (教师必填，唯一)
    teacher_no: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)

    # 学号 (学生必填，唯一)
    student_no: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)

    # 导师工号 (学生必填，关联导师的 teacher_no)
    advisor_no: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # 单位名称 (校外人员必填)
    org_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # -------------------------------------------------------------------------
    # 状态与元数据
    # -------------------------------------------------------------------------

    # 账号是否启用
    # False 表示账号被禁用，无法登录
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
