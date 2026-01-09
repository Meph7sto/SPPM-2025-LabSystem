from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用全局配置类。

    该类使用 Pydantic BaseSettings 从环境变量或 .env 文件加载配置。
    涵盖了应用基本信息、安全设置、数据库连接以及业务相关的定时任务配置。
    """

    # -------------------------------------------------------------------------
    # 应用基本配置
    # -------------------------------------------------------------------------

    # 应用名称，用于 Swagger 文档标题和日志标识
    app_name: str = Field("LESMS", alias="APP_NAME")

    # 运行环境：dev (开发), prod (生产), test (测试)
    # 不同的环境可能会影响日志级别、调试模式等行为
    env: str = Field("dev", alias="APP_ENV")

    # API 路径前缀，所有 API 路由都会包含此前缀
    api_prefix: str = Field("/api/v1", alias="API_PREFIX")

    # -------------------------------------------------------------------------
    # 安全配置 (JWT & CORS)
    # -------------------------------------------------------------------------

    # JWT 签名密钥，生产环境必须修改为强随机字符串
    jwt_secret: str = Field("change-me", alias="JWT_SECRET")

    # JWT 访问令牌过期时间（分钟），默认 60 分钟
    jwt_expire_minutes: int = Field(60, alias="JWT_EXPIRE_MINUTES")

    # 允许访问管理接口的 IP 白名单 (CIDR 格式)
    # 用于限制敏感操作（如系统配置）的来源 IP
    allowed_admin_ips: str = Field("127.0.0.1/32", alias="ALLOWED_ADMIN_IPS")

    # CORS (跨域资源共享) 允许的源列表，多个源用逗号分隔
    # 前端开发服务器通常运行在 5173 端口
    cors_origins: str = Field(
        "http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    # -------------------------------------------------------------------------
    # 数据库配置
    # -------------------------------------------------------------------------

    # 数据库连接 URL，默认为 SQLite
    # 格式示例: sqlite:///./data/lesms.db 或 postgresql://user:pass@localhost/dbname
    db_url: str = Field("sqlite:///./data/lesms.db", alias="DB_URL")

    # -------------------------------------------------------------------------
    # 业务功能配置
    # -------------------------------------------------------------------------

    # 是否启用财务系统 Mock
    # 如果启用，涉及到支付的逻辑会使用模拟实现，而非调用真实外部接口
    finance_mock_enabled: bool = Field(True, alias="FINANCE_MOCK_ENABLED")

    # 周报定时任务 Cron 表达式 (默认: 每周一 00:00)
    cron_report_weekly: str = Field("0 0 * * 1", alias="CRON_REPORT_WEEKLY")

    # 月报定时任务 Cron 表达式 (默认: 每月1号 00:00)
    cron_report_monthly: str = Field("0 0 1 * *", alias="CRON_REPORT_MONTHLY")

    # 年报定时任务 Cron 表达式 (默认: 每年1月1号 00:00)
    cron_report_yearly: str = Field("0 0 1 1 *", alias="CRON_REPORT_YEARLY")

    # Pydantic 配置
    model_config = SettingsConfigDict(
        env_file=".env",            # 指定环境变量文件
        env_file_encoding="utf-8",  # 文件编码
        extra="ignore",             # 忽略多余的环境变量
    )

    @field_validator("db_url")
    @classmethod
    def normalize_db_url(cls, value: str) -> str:
        """
        标准化 SQLite 数据库 URL，确保使用绝对路径。

        SQLite 在使用相对路径时（如 sqlite:///./data.db），其解析依赖于当前工作目录。
        为了保证在不同目录下运行应用（如测试、脚本、Docker）都能正确找到数据库文件，
        这里将相对路径转换为基于项目根目录的绝对路径。

        Args:
            value (str): 原始数据库 URL

        Returns:
            str: 标准化后的数据库 URL
        """
        # 内存数据库无需处理
        if value == "sqlite:///:memory:":
            return value

        # 检查是否为 SQLite URL 且非绝对路径（sqlite://// 表示绝对路径）
        if value.startswith("sqlite:///") and not value.startswith("sqlite:////"):
            path_part = value.replace("sqlite:///", "", 1)

            # 移除开头的相对路径符号 ./ 或 .\
            if path_part.startswith("./") or path_part.startswith(".\\"):
                path_part = path_part[2:]

            path = Path(path_part)

            # 如果解析出的路径不是绝对路径，则将其转换为基于项目根目录的绝对路径
            if not path.is_absolute():
                # 计算项目根目录
                # __file__ 是当前文件 (config.py) 的路径
                # parents[3] 对应: backend/app/core/config.py -> backend/
                base_dir = Path(__file__).resolve().parents[3]
                path = base_dir / path

            # 重新组装 URL，注意 Windows 下的反斜杠替换为正斜杠
            normalized = str(path).replace("\\", "/")
            return f"sqlite:///{normalized}"

        return value


# 创建全局配置实例，供其他模块导入使用
settings = Settings()
