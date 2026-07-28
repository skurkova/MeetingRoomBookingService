from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.time_slot import TimeSlotResponse


class RoomSlotResponse(BaseModel):
    """Схема для отображения информации о временных слотах переговорной комнаты"""

    id: int
    room_id: int
    time_slot: TimeSlotResponse

    model_config = ConfigDict(from_attributes=True)


class RoomSlotAvailableResponse(RoomSlotResponse):
    """
    Схема для отображения информации о доступных временных слотах
    переговорной комнаты
    """

    is_available: bool = True

    model_config = ConfigDict(from_attributes=True)


class RoomResponse(BaseModel):
    """Схема для отображения информации переговорной комнаты"""

    id: int
    name: str
    room_slots: List[RoomSlotResponse]

    model_config = ConfigDict(from_attributes=True)


class RoomAvailableResponse(BaseModel):
    """Схема для отображения информации доступности переговорной комнаты"""

    id: int
    name: str
    room_slots: List[RoomSlotAvailableResponse]

    model_config = ConfigDict(from_attributes=True)
