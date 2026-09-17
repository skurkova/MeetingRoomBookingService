from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.logging import get_logger
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.utils.get_current_user import get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])
logger = get_logger(__name__)


@router.get("/", response_model=List[BookingResponse], status_code=status.HTTP_200_OK)
async def get_bookings(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """Получение списка бронирований переговорных комнат"""

    result = await db.execute(select(Booking))
    bookings = result.scalars().all()

    if not user.is_admin:
        bookings = [booking for booking in bookings if booking.user_id == user.id]
    return bookings


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Забронировать временный слот переговорной комнаты"""

    result = await db.execute(
        select(Booking).where(
            Booking.room_slot_id == booking_data.room_slot_id,
            Booking.booking_date == booking_data.booking_date,
        )
    )
    booking_exist = result.scalars().one_or_none()

    if booking_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is already for this datetime booking",
        )

    booking = Booking(
        user_id=user.id,
        room_slot_id=booking_data.room_slot_id,
        booking_date=booking_data.booking_date,
    )
    db.add(booking)
    await logger.info(
        "Time slot meeting room slot successfully reserved",
        user_id=user.id,
        room_slot_id=booking.room_slot_id,
        booking_date=booking.booking_date,
    )
    await db.commit()
    await db.refresh(booking)

    return booking


@router.get(
    "/{booking_id}", response_model=BookingResponse, status_code=status.HTTP_200_OK
)
async def get_booking_id(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Получить бронирование по ID"""

    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    if not user.is_admin and user.id != booking.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN for this user"
        )

    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking_id(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Отменить бронирование"""

    booking_result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = booking_result.scalars().one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    if not user.is_admin and booking.user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN for this user"
        )

    await db.delete(booking)
    await logger.info(
        "Booking successfully canceled", user_id=user.id, booking_id=booking_id
    )
    await db.commit()
