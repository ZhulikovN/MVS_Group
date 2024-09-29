# pylint: disable=invalid-name
from typing import AsyncGenerator, Callable, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.api.app import app
from src.bd.database import get_db
from src.settings import settings
from tests.database import DBTest

NEW_DB_NAME = "db_tests"

settings.DB_HOST = "localhost"
settings.DB_PORT = 5432
settings.DB_USER = "user"
settings.DB_NAME = NEW_DB_NAME
settings.DB_PASSWORD = "password"
settings.redis_host = "localhost"


@pytest.fixture(scope="module")
def setup_database() -> Generator[None, None, None]:
    db_test = DBTest(settings.DB_NAME)
    db_test.setup_database()
    yield
    db_test.drop_database()


@pytest.fixture(scope="module")
def test_engine(setup_database: None) -> AsyncEngine:
    test_engine = create_async_engine(
        (
            f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        ),
        echo=True,
    )
    return test_engine


@pytest.fixture(scope="module")
def override_get_db(
    test_engine: AsyncEngine,
) -> Generator[Callable[[], AsyncGenerator[AsyncSession, None]], None, None]:
    TestSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore

    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db
    yield get_test_db
    del app.dependency_overrides[get_db]


@pytest.fixture
def client(override_get_db: None) -> Generator[TestClient, None, None]:
    with TestClient(app) as clients:
        yield clients


@pytest.fixture(scope="function")
async def async_client(override_get_db: None) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session(
    override_get_db: Callable[[], AsyncGenerator[AsyncSession, None]],
) -> AsyncGenerator[AsyncSession, None]:
    async for session in override_get_db():
        yield session
