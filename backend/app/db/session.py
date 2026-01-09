from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

db_url = settings.db_url
connect_args: dict[str, object] = {}
# SQLite 特定的连接参数
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # 确保数据库目录存在
    url = make_url(db_url)
    if url.database and url.database != ":memory:":
        Path(url.database).expanduser().parent.mkdir(parents=True, exist_ok=True)

# 创建数据库引擎
engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
# 创建会话工厂
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """
    数据库会话依赖项。
    用于 FastAPI 依赖注入，确保每个请求使用独立的数据库会话，并在请求结束后关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
