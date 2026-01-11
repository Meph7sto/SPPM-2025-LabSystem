from __future__ import annotations

from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    """用户个人资料更新请求"""

    name: str | None = Field(None, min_length=1, max_length=64, description="姓名")
    contact: str | None = Field(None, min_length=1, max_length=64, description="联系方式")
    college: str | None = Field(None, max_length=128, description="学院/单位（教师/学生）")
    org_name: str | None = Field(None, max_length=128, description="单位名称（校外人员）")
    # 注意：工号/学号等敏感字段不允许用户自行修改，需要管理员修改

