import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from movie_booking_api.db.base_class import Base


class Show(Base):
    __tablename__ = "shows"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    movie_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    screen_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("screens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ticket_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Show id={self.id} movie_id={self.movie_id} screen_id={self.screen_id}>"
