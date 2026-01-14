from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from ..db.base import Base


class SystemConfig(Base):
    """系统配置表模型"""
    __tablename__ = "system_config"

    # 配置键，例如: approval.external.chain
    key = Column(String(100), primary_key=True)

    # 配置值
    value = Column(Text, nullable=True)

    # 配置描述
    description = Column(String(255))

    # 创建时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 更新时间
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SystemConfig(key={self.key}, value={self.value[:50] if self.value else None})>"