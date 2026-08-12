# Database engine, session factory, and Base for Face Attendance app
import os
from dotenv import load_dotenv
load_dotenv('.env_22412b214a31e30d', override=True)

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

DEFAULT_DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@localhost:5432/gen_f07875928c"


def _to_async_url(url: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg:// if not already async."""
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


DATABASE_URL = _to_async_url(os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))

# Use NullPool during testing to avoid holding idle connections against
# a shared PostgreSQL server with limited max_connections.
import os as _os
_testing = _os.getenv("TESTING", "0") == "1"

if _testing:
    from sqlalchemy.pool import NullPool
    engine = create_async_engine(
        DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=2,
        max_overflow=3,
        echo=False,
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
