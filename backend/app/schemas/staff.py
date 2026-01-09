from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from ..models.user import BorrowerType, UserRole


class StaffBase(BaseModel):
    """
    人员台账基础属性模型。
    """
    name: str = Field(..., min_length=1, max_length=64, description="真实姓名")
    contact: str = Field(..., min_length=1, max_length=64, description="联系方式")


# -------------------------------------------------------------------------
# 教师相关 Schema
# -------------------------------------------------------------------------

class TeacherCreate(StaffBase):
    """
    创建教师请求模型。
    """
    teacher_no: str = Field(..., max_length=32, description="教师工号（唯一）")
    college: str = Field(..., max_length=128, description="所属学院")
    password: str = Field(default="12345678", min_length=8, description="初始密码，默认 12345678")


class TeacherUpdate(BaseModel):
    """
    更新教师请求模型。
    """
    name: str | None = Field(None, min_length=1, max_length=64)
    contact: str | None = Field(None, min_length=1, max_length=64)
    college: str | None = Field(None, max_length=128)
    is_active: bool | None = Field(None, description="是否启用账号")


class TeacherOut(BaseModel):
    """
    教师信息响应模型。
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    account: str
    teacher_no: str | None
    name: str
    contact: str
    college: str | None
    is_active: bool
    created_at: datetime


# -------------------------------------------------------------------------
# 学生相关 Schema
# -------------------------------------------------------------------------

class StudentCreate(StaffBase):
    """
    创建学生请求模型。
    """
    student_no: str = Field(..., max_length=32, description="学号（唯一）")
    advisor_no: str = Field(..., max_length=32, description="导师工号（必须存在）")
    college: str = Field(..., max_length=128, description="所属学院")
    password: str = Field(default="12345678", min_length=8, description="初始密码，默认 12345678")


class StudentUpdate(BaseModel):
    """
    更新学生请求模型。
    """
    name: str | None = Field(None, min_length=1, max_length=64)
    contact: str | None = Field(None, min_length=1, max_length=64)
    college: str | None = Field(None, max_length=128)
    advisor_no: str | None = Field(None, max_length=32, description="导师工号")
    is_active: bool | None = Field(None, description="是否启用账号")


class StudentOut(BaseModel):
    """
    学生信息响应模型。
    """
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


# -------------------------------------------------------------------------
# 校外人员相关 Schema
# -------------------------------------------------------------------------

class ExternalCreate(StaffBase):
    """
    创建校外人员请求模型。
    """
    org_name: str = Field(..., max_length=128, description="单位名称")
    password: str = Field(default="12345678", min_length=8, description="初始密码，默认 12345678")


class ExternalUpdate(BaseModel):
    """
    更新校外人员请求模型。
    """
    name: str | None = Field(None, min_length=1, max_length=64)
    contact: str | None = Field(None, min_length=1, max_length=64)
    org_name: str | None = Field(None, max_length=128)
    is_active: bool | None = Field(None, description="是否启用账号")


class ExternalOut(BaseModel):
    """
    校外人员信息响应模型。
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    account: str
    name: str
    contact: str
    org_name: str | None
    is_active: bool
    created_at: datetime


# -------------------------------------------------------------------------
# 聚合列表 Schema
# -------------------------------------------------------------------------

class StaffListResponse(BaseModel):
    """
    人员台账聚合列表响应模型。
    (目前 API 设计可能倾向于分开获取，此模型保留用于可能的聚合接口)
    """
    teachers: list[TeacherOut] = []
    students: list[StudentOut] = []
    externals: list[ExternalOut] = []
    total_teachers: int = 0
    total_students: int = 0
    total_externals: int = 0
