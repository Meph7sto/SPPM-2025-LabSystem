from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from ...db.session import get_db
from ...models.system_config import SystemConfig
from datetime import datetime

router = APIRouter()


@router.get("/system-config", response_model=Dict[str, Optional[str]])
async def get_all_config(db: Session = Depends(get_db)):
    """
    获取所有系统配置
    返回格式：{"配置键1": "值1", "配置键2": "值2", ...}
    """
    configs = db.query(SystemConfig).all()
    return {config.key: config.value for config in configs}


@router.put("/system-config")
async def update_config(
        config_data: Dict[str, Optional[str]],  # ← 修复这里的缩进
        db: Session = Depends(get_db)
):
    """
    批量更新系统配置
    输入格式：{"配置键1": "新值1", "配置键2": "新值2"}
    """
    for key, value in config_data.items():
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = value
            config.updated_at = datetime.utcnow()
        else:
            config = SystemConfig(
                key=key,
                value=value,
                description=f"系统配置项: {key}"
            )
            db.add(config)

    db.commit()
    updated_count = len(config_data)
    return {
        "message": f"成功更新 {updated_count} 个配置项",
        "updated_count": updated_count
    }