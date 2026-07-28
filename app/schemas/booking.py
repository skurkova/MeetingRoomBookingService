from pydantic import BaseModel, ConfigDict
from datetime import date

from app.schemas.user import UserResponse
from app.schemas.room import RoomSlotResponse


class BookingCreate(BaseModel):
    """Схема для создания бронирования переговорной комнаты"""

    room_slot_id: int
    booking_date: date


class BookingResponse(BaseModel):
    """Схема ответа для бронирования переговорной комнаты"""

    id: int
    user: UserResponse
    room_slot: RoomSlotResponse
    booking_date: date

    model_config = ConfigDict(from_attributes=True)

