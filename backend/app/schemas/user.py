from __future__ import annotations

from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    """
    用户个人资料更新请求模型。
    用户只能修改基本联系信息，工号/学号等身份信息不可变更。
    """

    name: str | None = Field(None, min_length=1, max_length=64, description="真实姓名")
    contact: str | None = Field(None, min_length=1, max_length=64, description="联系方式")
    college: str | None = Field(None, max_length=128, description="学院/单位（仅教师/学生可填）")
    org_name: str | None = Field(None, max_length=128, description="单位名称（仅校外人员可填）")
    # 注意：工号/学号等敏感字段不允许用户自行修改，需要管理员修改
