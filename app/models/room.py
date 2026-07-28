from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Room(Base):
    """Переговорная комната"""

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    room_slots: Mapped[List["RoomSlot"]] = relationship(
        back_populates="room", cascade="all,  delete-orphan", lazy="selectin"
    )


class RoomSlot(Base):
    """Слот переговорной комнаты"""

    __tablename__ = "room_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    time_slot_id: Mapped[int] = mapped_column(
        ForeignKey("time_slots.id", ondelete="CASCADE")
    )

    room: Mapped["Room"] = relationship(back_populates="room_slots", lazy="joined")
    time_slot: Mapped["TimeSlot"] = relationship(lazy="joined")
    bookings: Mapped[List["Booking"]] = relationship(
        back_populates="room_slot", lazy="selectin"
    )
