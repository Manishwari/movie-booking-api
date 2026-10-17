from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.seats.exceptions import SeatNotFoundError
from movie_booking_api.seats.models import Seat
from movie_booking_api.seats.schemas import SeatCreate, SeatUpdate


async def list_seats(
    db: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Seat]:
    stmt = select(Seat).order_by(Seat.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_seat(
    db: AsyncSession,
    seat_id: uuid.UUID,
) -> Seat:
    seat = await db.get(Seat, seat_id)

    if seat is None:
        raise SeatNotFoundError(seat_id)

    return seat


async def create_seat(
    db: AsyncSession,
    data: SeatCreate,
) -> Seat:
    seat = Seat(**data.model_dump())

    db.add(seat)

    await db.commit()
    await db.refresh(seat)

    return seat


async def update_seat(
    db: AsyncSession,
    seat_id: uuid.UUID,
    data: SeatUpdate,
) -> Seat:
    seat = await get_seat(db, seat_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(seat, field, value)

    await db.commit()
    await db.refresh(seat)

    return seat


async def delete_seat(
    db: AsyncSession,
    seat_id: uuid.UUID,
) -> None:
    seat = await get_seat(db, seat_id)

    await db.delete(seat)
    await db.commit()
