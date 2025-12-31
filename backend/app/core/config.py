from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("LESMS", alias="APP_NAME")
    env: str = Field("dev", alias="APP_ENV")
    api_prefix: str = Field("/api/v1", alias="API_PREFIX")
    jwt_secret: str = Field("change-me", alias="JWT_SECRET")
    jwt_expire_minutes: int = Field(60, alias="JWT_EXPIRE_MINUTES")
    db_url: str = Field("sqlite:///./data/lesms.db", alias="DB_URL")
    finance_mock_enabled: bool = Field(True, alias="FINANCE_MOCK_ENABLED")
    cron_report_weekly: str = Field("0 0 * * 1", alias="CRON_REPORT_WEEKLY")
    cron_report_monthly: str = Field("0 0 1 * *", alias="CRON_REPORT_MONTHLY")
    cron_report_yearly: str = Field("0 0 1 1 *", alias="CRON_REPORT_YEARLY")
    allowed_admin_ips: str = Field("127.0.0.1/32", alias="ALLOWED_ADMIN_IPS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("db_url")
    @classmethod
    def normalize_db_url(cls, value: str) -> str:
        if value == "sqlite:///:memory:":
            return value
        if value.startswith("sqlite:///") and not value.startswith("sqlite:////"):
            path_part = value.replace("sqlite:///", "", 1)
            if path_part.startswith("./") or path_part.startswith(".\\"):
                path_part = path_part[2:]
            path = Path(path_part)
            if not path.is_absolute():
                base_dir = Path(__file__).resolve().parents[3]
                path = base_dir / path
            normalized = str(path).replace("\\", "/")
            return f"sqlite:///{normalized}"
        return value


settings = Settings()
