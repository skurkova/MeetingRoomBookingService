from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import engine, Base, async_session
from app.utils.init_db_data import db_init_data
from app.routers import auth, rooms, bookings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        await db_init_data(session)

    yield

    await engine.dispose()


app = FastAPI(
    title="Meeting Room Booking Service",
    description="Сервис бронирования переговорных комнат",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
