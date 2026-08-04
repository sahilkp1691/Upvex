from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


# statement_cache_size=0 keeps asyncpg compatible with Supabase's pgbouncer
# (transaction-mode pooling breaks prepared statements).
# timeout avoids hanging forever on a bad DATABASE_URL (Railway healthcheck).
connect_args = {}
if settings.database_url.startswith("postgresql+asyncpg"):
    connect_args = {"statement_cache_size": 0, "timeout": 15}

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args=connect_args,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with async_session_factory() as session:
        yield session
