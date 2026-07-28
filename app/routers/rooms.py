from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.booking import Booking
from app.models.room import Room, RoomSlot
from app.schemas.room import RoomAvailableResponse, RoomSlotAvailableResponse

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get(
    "/", response_model=List[RoomAvailableResponse], status_code=status.HTTP_200_OK
)
async def get_rooms(
    target_date: date | None = Query(
        None, description="Фильтр слотов по дате (YYYY-MM-DD)"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Получить список всех комнат с их временными слотами"""

    booking_date = target_date or date.today()
    bookings_for_date_result = await db.execute(
        select(Booking.room_slot_id).where(Booking.booking_date == booking_date)
    )
    booking_room_slots_ids = bookings_for_date_result.scalars().all()

    rooms_result = await db.execute(select(Room))
    rooms = rooms_result.scalars().all()

    rooms_is_available_slots = []
    for room in rooms:
        room_slots = []
        for room_slot in room.room_slots:
            room_slots.append(
                RoomSlotAvailableResponse(
                    id=room_slot.id,
                    room_id=room.id,
                    time_slot=room_slot.time_slot,
                    is_available=room_slot.id not in booking_room_slots_ids,
                )
            )
        rooms_is_available_slots.append(
            RoomAvailableResponse(id=room.id, name=room.name, room_slots=room_slots)
        )

    return rooms_is_available_slots


@router.get(
    "/{room_id}", response_model=RoomAvailableResponse, status_code=status.HTTP_200_OK
)
async def get_room_id(
    room_id: int,
    target_date: date | None = Query(
        None, description="Фильтр слотов по дате (YYYY-MM-DD)"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Получить комнату с временными слотами"""

    booking_date = target_date or date.today()
    bookings_room_for_date_result = await db.execute(
        select(Booking.room_slot_id)
        .join(Booking.room_slot)
        .where(Booking.booking_date == booking_date, RoomSlot.room_id == room_id)
    )
    booking_room_slots_ids = bookings_room_for_date_result.scalars().all()

    room_result = await db.execute(select(Room).where(Room.id == room_id))
    room = room_result.scalars().one_or_none()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )

    room_slots = []
    for room_slot in room.room_slots:
        room_slots.append(
            RoomSlotAvailableResponse(
                id=room_slot.id,
                room_id=room.id,
                time_slot=room_slot.time_slot,
                is_available=room_slot.id not in booking_room_slots_ids,
            )
        )

    return RoomAvailableResponse(id=room.id, name=room.name, room_slots=room_slots)
