from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging import get_logger
from app.models.room import Room, RoomSlot
from app.models.time_slot import TimeSlot
from app.models.user import User
from app.utils.security_password import hash_the_password

logger = get_logger(__name__)

USERS = [
    {
        "username": "admin",
        "full_name": "Admin Admin",
        "email": "admin@exemple.ru",
        "password": "admin123",
        "is_admin": True,
    },
    {
        "username": "employee_1",
        "full_name": "Employee 1",
        "email": "employee1@exemple.ru",
        "password": "employee1_123",
        "is_admin": False,
    },
    {
        "username": "employee_2",
        "full_name": "Employee 2",
        "email": "employee2@exemple.ru",
        "password": "employee2_123",
        "is_admin": False,
    },
    {
        "username": "employee_3",
        "full_name": "Employee 3",
        "email": "employee3@exemple.ru",
        "password": "employee3_123",
        "is_admin": False,
    },
]

ROOMS = [
    {"name": "Переговорная 1"},
    {"name": "Переговорная 2"},
    {"name": "Переговорная 3"},
]

TIME_SLOTS = [
    {"start_time": time(9, 0), "end_time": time(11, 0)},
    {"start_time": time(12, 0), "end_time": time(14, 0)},
    {"start_time": time(15, 0), "end_time": time(17, 0)},
    {"start_time": time(18, 0), "end_time": time(20, 0)},
]


async def db_init_data(db: AsyncSession):
    """Заполняем БД: пользователями, переговорными комнатами и временными слотами"""

    await logger.info("Database tables data initialized started")
    exist_users = await db.execute(select(User))
    if exist_users.scalars().first() is not None:
        return

    users = [
        User(
            username=user["username"],
            full_name=user["full_name"],
            email=user["email"],
            password_hash=hash_the_password(str(user["password"])),
            is_admin=user["is_admin"],
        )
        for user in USERS
    ]
    db.add_all(users)
    await logger.info("Users initialized successfully in the database")

    exist_rooms = await db.execute(select(Room))
    if exist_rooms.scalars().first() is not None:
        return

    rooms = [Room(name=room["name"]) for room in ROOMS]
    db.add_all(rooms)
    await logger.info("Rooms initialized successfully in the database")

    exist_time_slots = await db.execute(select(TimeSlot))
    if exist_time_slots.scalars().first() is not None:
        return

    time_slots = [
        TimeSlot(start_time=time_slot["start_time"], end_time=time_slot["end_time"])
        for time_slot in TIME_SLOTS
    ]
    db.add_all(time_slots)
    await logger.info("Time slots initialized successfully in the database")
    await db.flush()

    room_slots = []
    for room in rooms:
        for time_slot in time_slots:
            room_slots.append(RoomSlot(room_id=room.id, time_slot_id=time_slot.id))
    db.add_all(room_slots)
    await logger.info("Room slots initialized successfully in the database")

    await db.commit()
