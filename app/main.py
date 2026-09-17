from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, async_session, engine
from app.logging import get_logger, setup_logging
from app.routers import auth, bookings, rooms
from app.utils.init_db_data import db_init_data

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await logger.info("Application startup initiated")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await logger.info("Database tables created")

    async with async_session() as session:
        await db_init_data(session)
    await logger.info("Database tables data initialized successfully")

    await logger.info("Application startup completed successfully")
    yield

    await logger.info("Application shutdown initiated")
    await engine.dispose()
    await logger.info("Application shutdown completed")


app = FastAPI(
    title="Meeting Room Booking Service",
    description="Сервис бронирования переговорных комнат",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
