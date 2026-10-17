import uuid

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from movie_booking_api.db.base_class import Base


class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    screen_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("screens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    seat_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Seat id={self.id} seat_number={self.seat_number!r}>"
