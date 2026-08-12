from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from src.conf import Config

DATABASE_URL = Config.DATABASE_URL

_engine_kwargs: dict = {"echo": Config.APP_ENV != "development"}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    if ":memory:" in DATABASE_URL or Config.APP_ENV == "development":
        _engine_kwargs["poolclass"] = StaticPool

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
