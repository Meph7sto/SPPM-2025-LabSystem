from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

# 获取数据库配置 URL
db_url = settings.db_url

# 数据库连接参数
connect_args: dict[str, object] = {}

# SQLite 特定的连接参数处理
if db_url.startswith("sqlite"):
    # check_same_thread=False 允许在多线程环境（如 FastAPI）中使用同一个 SQLite 连接
    connect_args = {"check_same_thread": False}

    # 确保数据库文件所在的目录存在
    url = make_url(db_url)
    if url.database and url.database != ":memory:":
        # 创建父目录（如果不存在）
        Path(url.database).expanduser().parent.mkdir(parents=True, exist_ok=True)

# 创建数据库引擎
# pool_pre_ping=True 启用连接存活检测，防止使用已关闭的连接
engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)

# 创建会话工厂 (SessionLocal)
# autocommit=False: 禁止自动提交，需要手动 commit，保证事务控制
# autoflush=False: 禁止自动刷新，需要手动 flush，防止意外的数据库写入
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """
    数据库会话依赖项生成器。

    用于 FastAPI 的依赖注入系统 (Depends)。
    它的作用是：
    1. 为每个请求创建一个新的数据库会话 (Session)。
    2. 在请求处理过程中提供该会话。
    3. 请求结束后（无论成功还是异常），确保关闭会话，释放连接资源。

    Yields:
        Session: SQLAlchemy 数据库会话对象。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
