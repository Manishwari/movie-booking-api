"""Business logic for the ``Show`` slice.

This module owns the transaction boundary and knows nothing about HTTP.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.shows.exceptions import ShowNotFoundError
from movie_booking_api.shows.models import Show
from movie_booking_api.shows.schemas import ShowCreate, ShowUpdate


async def list_shows(
    db: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Show]:
    stmt = select(Show).order_by(Show.start_time.asc()).limit(limit).offset(offset)

    result = await db.execute(stmt)

    return result.scalars().all()


async def get_show(
    db: AsyncSession,
    show_id: uuid.UUID,
) -> Show:
    show = await db.get(Show, show_id)

    if show is None:
        raise ShowNotFoundError(show_id)

    return show


async def create_show(
    db: AsyncSession,
    data: ShowCreate,
) -> Show:
    show = Show(**data.model_dump())

    db.add(show)
    await db.commit()

    await db.refresh(show)

    return show


async def update_show(
    db: AsyncSession,
    show_id: uuid.UUID,
    data: ShowUpdate,
) -> Show:
    show = await get_show(db, show_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(show, field, value)

    await db.commit()
    await db.refresh(show)

    return show


async def delete_show(
    db: AsyncSession,
    show_id: uuid.UUID,
) -> None:
    show = await get_show(db, show_id)

    await db.delete(show)
    await db.commit()
