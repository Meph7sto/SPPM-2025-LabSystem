from __future__ import annotations

import enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..models.user import BorrowerType, UserRole


class LoginRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"
    EXTERNAL = "external"
    ADMIN = "admin"
    HEAD = "head"


class RegisterRequest(BaseModel):
    role: BorrowerType
    name: str = Field(min_length=1)
    contact: str = Field(min_length=1)
    college: str | None = None
    teacher_no: str | None = None
    student_no: str | None = None
    advisor_no: str | None = None
    org_name: str | None = None
    password: str = Field(min_length=8)

    @model_validator(mode="after")
    def check_role_fields(self) -> "RegisterRequest":
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
    account: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: LoginRole


class UserOut(BaseModel):
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
    access_token: str
    token_type: str
    user: UserOut
