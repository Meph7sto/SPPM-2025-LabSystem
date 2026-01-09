from __future__ import annotations

import enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..models.user import BorrowerType, UserRole


class LoginRole(str, enum.Enum):
    """登录角色"""
    TEACHER = "teacher"    # 教师
    STUDENT = "student"    # 学生
    EXTERNAL = "external"  # 校外人员
    ADMIN = "admin"        # 管理员
    HEAD = "head"          # 负责人


class RegisterRequest(BaseModel):
    """注册请求模型"""
    role: BorrowerType = Field(..., description="注册角色类型")
    name: str = Field(..., min_length=1, description="真实姓名")
    contact: str = Field(..., min_length=1, description="联系方式")
    college: str | None = Field(None, description="学院（教师/学生必填）")
    teacher_no: str | None = Field(None, description="教师工号（教师必填）")
    student_no: str | None = Field(None, description="学号（学生必填）")
    advisor_no: str | None = Field(None, description="导师工号（学生必填）")
    org_name: str | None = Field(None, description="单位名称（校外人员必填）")
    password: str = Field(..., min_length=8, description="密码（最少8位）")

    @model_validator(mode="after")
    def check_role_fields(self) -> "RegisterRequest":
        """
        根据角色校验必填字段。
        - 教师：工号、学院
        - 学生：学号、导师工号、学院
        - 校外人员：单位名称
        """
        if self.role == BorrowerType.TEACHER:
            if not self.teacher_no:
                raise ValueError("teacher_no is required for teacher")
            if not self.college:
                raise ValueError("college is required for teacher")
        elif self.role == BorrowerType.STUDENT:
            if not self.student_no:
                raise ValueError("student_no is required for student")
            if not self.advisor_no:
                raise ValueError("advisor_no is required for student")
            if not self.college:
                raise ValueError("college is required for student")
        elif self.role == BorrowerType.EXTERNAL:
            if not self.org_name:
                raise ValueError("org_name is required for external")
        return self


class LoginRequest(BaseModel):
    """登录请求模型"""
    account: str = Field(..., min_length=1, description="账号")
    password: str = Field(..., min_length=1, description="密码")
    role: LoginRole = Field(..., description="登录角色")


class UserOut(BaseModel):
    """用户公开信息模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    account: str
    role: UserRole
    borrower_type: BorrowerType | None
    name: str
    contact: str
    college: str | None
    teacher_no: str | None
    student_no: str | None
    advisor_no: str | None
    org_name: str | None


class TokenResponse(BaseModel):
    """登录成功响应模型"""
    access_token: str
    token_type: str
    user: UserOut
