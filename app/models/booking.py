from datetime import date

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Booking(Base):
    """Бронирование переговорной комнаты"""

    __tablename__ = "booking"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    room_slot_id: Mapped[int] = mapped_column(
        ForeignKey("room_slots.id", ondelete="CASCADE")
    )
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)

    user: Mapped["User"] = relationship(back_populates="bookings", lazy="joined")
    room_slot: Mapped["RoomSlot"] = relationship(
        back_populates="bookings", lazy="joined"
    )
