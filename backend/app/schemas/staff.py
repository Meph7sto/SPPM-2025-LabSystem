from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from ..models.user import BorrowerType, UserRole


class StaffBase(BaseModel):
    """人员台账基础字段"""
    name: str = Field(..., min_length=1, max_length=64, description="姓名")
    contact: str = Field(..., min_length=1, max_length=64, description="联系方式")


class TeacherCreate(StaffBase):
    """教师台账创建"""
    teacher_no: str = Field(..., max_length=32, description="教师工号")
    college: str = Field(..., max_length=128, description="学院")
    password: str = Field(default="12345678", min_length=8, description="初始密码")


class TeacherUpdate(BaseModel):
    """教师台账更新"""
    name: str | None = Field(None, min_length=1, max_length=64)
    contact: str | None = Field(None, min_length=1, max_length=64)
    college: str | None = Field(None, max_length=128)
    is_active: bool | None = None


class TeacherOut(BaseModel):
    """教师台账输出"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    account: str
    teacher_no: str | None
    name: str
    contact: str
    college: str | None
    is_active: bool
    created_at: datetime


class StudentCreate(StaffBase):
    """学生台账创建"""
    student_no: str = Field(..., max_length=32, description="学号")
    advisor_no: str = Field(..., max_length=32, description="导师工号")
    college: str = Field(..., max_length=128, description="学院")
    password: str = Field(default="12345678", min_length=8, description="初始密码")


class StudentUpdate(BaseModel):
    """学生台账更新"""
    name: str | None = Field(None, min_length=1, max_length=64)
    contact: str | None = Field(None, min_length=1, max_length=64)
    college: str | None = Field(None, max_length=128)
    advisor_no: str | None = Field(None, max_length=32)
    is_active: bool | None = None


class StudentOut(BaseModel):
    """学生台账输出"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    account: str
    student_no: str | None
    advisor_no: str | None
    name: str
    contact: str
    college: str | None
    is_active: bool
    created_at: datetime


class ExternalCreate(StaffBase):
    """校外人员台账创建"""
    org_name: str = Field(..., max_length=128, description="单位名称")
    password: str = Field(default="12345678", min_length=8, description="初始密码")


class ExternalUpdate(BaseModel):
    """校外人员台账更新"""
    name: str | None = Field(None, min_length=1, max_length=64)
    contact: str | None = Field(None, min_length=1, max_length=64)
    org_name: str | None = Field(None, max_length=128)
    is_active: bool | None = None


class ExternalOut(BaseModel):
    """校外人员台账输出"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    account: str
    name: str
    contact: str
    org_name: str | None
    is_active: bool
    created_at: datetime


class StaffListResponse(BaseModel):
    """人员台账列表响应"""
    teachers: list[TeacherOut] = []
    students: list[StudentOut] = []
    externals: list[ExternalOut] = []
    total_teachers: int = 0
    total_students: int = 0
    total_externals: int = 0
