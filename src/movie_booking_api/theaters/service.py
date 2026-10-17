"""Business logic for the ``Theater`` slice.

This module owns the transaction boundary and knows nothing about HTTP.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.theaters.exceptions import TheaterNotFoundError
from movie_booking_api.theaters.models import Theater
from movie_booking_api.theaters.schemas import TheaterCreate, TheaterUpdate


async def list_theaters(
    db: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Theater]:
    stmt = select(Theater).order_by(Theater.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_theater(
    db: AsyncSession,
    theater_id: uuid.UUID,
) -> Theater:
    theater = await db.get(Theater, theater_id)

    if theater is None:
        raise TheaterNotFoundError(theater_id)

    return theater


async def create_theater(
    db: AsyncSession,
    data: TheaterCreate,
) -> Theater:
    theater = Theater(**data.model_dump())

    db.add(theater)
    await db.commit()

    await db.refresh(theater)

    return theater


async def update_theater(
    db: AsyncSession,
    theater_id: uuid.UUID,
    data: TheaterUpdate,
) -> Theater:
    theater = await get_theater(db, theater_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(theater, field, value)

    await db.commit()
    await db.refresh(theater)

    return theater


async def delete_theater(
    db: AsyncSession,
    theater_id: uuid.UUID,
) -> None:
    theater = await get_theater(db, theater_id)

    await db.delete(theater)
    await db.commit()
