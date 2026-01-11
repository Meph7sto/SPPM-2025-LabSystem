from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类，从环境变量加载配置。
    使用 Pydantic Settings 进行管理。
    """
    # 应用名称
    app_name: str = Field("LESMS", alias="APP_NAME")
    # 运行环境：dev, prod, test
    env: str = Field("dev", alias="APP_ENV")
    # API 路径前缀
    api_prefix: str = Field("/api/v1", alias="API_PREFIX")
    # JWT 签名密钥
    jwt_secret: str = Field("change-me", alias="JWT_SECRET")
    # JWT 过期时间（分钟）
    jwt_expire_minutes: int = Field(60, alias="JWT_EXPIRE_MINUTES")
    # 数据库连接 URL
    db_url: str = Field("sqlite:///./data/lesms.db", alias="DB_URL")
    # 是否启用财务系统 Mock
    finance_mock_enabled: bool = Field(True, alias="FINANCE_MOCK_ENABLED")
    # 周报定时任务 Cron 表达式
    cron_report_weekly: str = Field("0 0 * * 1", alias="CRON_REPORT_WEEKLY")
    # 月报定时任务 Cron 表达式
    cron_report_monthly: str = Field("0 0 1 * *", alias="CRON_REPORT_MONTHLY")
    # 年报定时任务 Cron 表达式
    cron_report_yearly: str = Field("0 0 1 1 *", alias="CRON_REPORT_YEARLY")
    # 允许访问管理接口的 IP 白名单 CIDR
    allowed_admin_ips: str = Field("127.0.0.1/32", alias="ALLOWED_ADMIN_IPS")
    # CORS 允许的源
    cors_origins: str = Field(
        "http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("db_url")
    @classmethod
    def normalize_db_url(cls, value: str) -> str:
        """
        标准化 SQLite 数据库 URL，确保使用绝对路径。
        解决相对路径在不同执行目录下可能不一致的问题。
        """
        if value == "sqlite:///:memory:":
            return value
        if value.startswith("sqlite:///") and not value.startswith("sqlite:////"):
            path_part = value.replace("sqlite:///", "", 1)
            # 移除开头的 ./ 或 .\
            if path_part.startswith("./") or path_part.startswith(".\\"):
                path_part = path_part[2:]
            path = Path(path_part)
            # 如果不是绝对路径，则将其转换为基于项目根目录的绝对路径
            if not path.is_absolute():
                # 假设 config.py 在 backend/app/core/，项目根目录为 backend 的上一级
                base_dir = Path(__file__).resolve().parents[3]
                path = base_dir / path
            normalized = str(path).replace("\\", "/")
            return f"sqlite:///{normalized}"
        return value


settings = Settings()
