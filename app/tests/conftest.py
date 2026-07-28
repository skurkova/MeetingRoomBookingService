import pytest_asyncio

from sqlalchemy import delete
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import ASGITransport, AsyncClient

from app.database import Base, get_db
from app.config import settings
from app.main import app as _app
from app.utils.init_db_data import db_init_data
from app.models.booking import Booking


DATABASE_URL_TEST = settings.test_db_url
# Используем NullPool, чтобы избежать проблем с event loop в асинхронных тестах
test_engine = create_async_engine(DATABASE_URL_TEST, echo=False, poolclass=NullPool)
async_session_test = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Переопределение зависимости get_db для тестов"""

    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture()
async def db_session():
    """Фикстура сессии для каждого теста """

    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db_test():
    """Создаем таблицы в тестовой БД перед запуском тестов и удаляем после"""

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_test() as session:
        await db_init_data(session)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def reset_bookings(db_session):
    """Очищает таблицу бронирований перед каждым тестом"""

    await db_session.execute(delete(Booking))
    await db_session.commit()
    yield


@pytest_asyncio.fixture
async def client(setup_db_test):
    """Фикстура асинхронного клиента с подмененной зависимостью БД"""

    _app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=_app), base_url="http://test") as ac:
        yield ac

    _app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def headers_admin_auth(client: AsyncClient):
    """Фикстура получения токена для авторизации админа"""

    admin_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = await client.post("/auth/login", data=admin_data)
    assert response.status_code == 200

    token = response.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture()
async def headers_employee_auth(client: AsyncClient):
    """Фикстура получения токена для авторизации сотрудника"""

    employee_data = {
        "username": "employee_1",
        "password": "employee1_123"
    }
    response = await client.post("/auth/login", data=employee_data)
    assert response.status_code == 200

    token = response.json()["access_token"]
    yield {"Authorization": f"Bearer {token}"}
