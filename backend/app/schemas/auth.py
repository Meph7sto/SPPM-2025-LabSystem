from __future__ import annotations

import enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..models.user import BorrowerType, UserRole


class LoginRole(str, enum.Enum):
    """
    登录时选择的角色枚举。
    前端登录界面提供的角色选项。
    """
    TEACHER = "teacher"    # 教师
    STUDENT = "student"    # 学生
    EXTERNAL = "external"  # 校外人员
    ADMIN = "admin"        # 管理员
    HEAD = "head"          # 负责人


class RegisterRequest(BaseModel):
    """
    用户注册请求数据模型。
    """
    role: BorrowerType = Field(..., description="注册角色类型 (teacher/student/external)")
    name: str = Field(..., min_length=1, description="真实姓名")
    contact: str = Field(..., min_length=1, description="联系方式 (电话或邮箱)")

    # 可选字段，根据角色不同进行验证
    college: str | None = Field(None, description="学院/部门（教师/学生必填）")
    teacher_no: str | None = Field(None, description="教师工号（教师必填）")
    student_no: str | None = Field(None, description="学号（学生必填）")
    advisor_no: str | None = Field(None, description="导师工号（学生必填）")
    org_name: str | None = Field(None, description="单位名称（校外人员必填）")

    password: str = Field(..., min_length=8, description="登录密码（最少8位）")

    @model_validator(mode="after")
    def check_role_fields(self) -> "RegisterRequest":
        """
        根据注册角色校验相应的必填字段。

        - 教师：必须提供工号 (teacher_no) 和学院 (college)。
        - 学生：必须提供学号 (student_no)、导师工号 (advisor_no) 和学院 (college)。
        - 校外人员：必须提供单位名称 (org_name)。

        Raises:
            ValueError: 如果缺少必填字段。
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
    """
    用户登录请求数据模型。
    """
    account: str = Field(..., min_length=1, description="登录账号")
    password: str = Field(..., min_length=1, description="登录密码")
    role: LoginRole = Field(..., description="登录时选择的角色身份")


class UserOut(BaseModel):
    """
    用户公开信息模型。
    用于响应中返回用户信息，隐藏敏感数据（如密码）。
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    account: str
    role: UserRole
    borrower_type: BorrowerType | None
    name: str
    contact: str

    # 详细信息
    college: str | None
    teacher_no: str | None
    student_no: str | None
    advisor_no: str | None
    org_name: str | None


class TokenResponse(BaseModel):
    """
    登录成功后的响应模型。
    包含 JWT 令牌和当前用户信息。
    """
    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(..., description="令牌类型 (Bearer)")
    user: UserOut = Field(..., description="当前登录用户的详细信息")
