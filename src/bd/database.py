from typing import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.settings import settings

redis_client: Redis = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db
)

engine: AsyncEngine = create_async_engine(settings.database_url, echo=True)  # type: ignore

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass
