"""Business logic for the ``Screen`` slice.

This module owns the transaction boundary and knows nothing about HTTP.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.screens.exceptions import ScreenNotFoundError
from movie_booking_api.screens.models import Screen
from movie_booking_api.screens.schemas import ScreenCreate, ScreenUpdate


async def list_screens(
    db: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Screen]:
    stmt = select(Screen).order_by(Screen.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)

    return result.scalars().all()


async def get_screen(
    db: AsyncSession,
    screen_id: uuid.UUID,
) -> Screen:
    screen = await db.get(Screen, screen_id)

    if screen is None:
        raise ScreenNotFoundError(screen_id)

    return screen


async def create_screen(
    db: AsyncSession,
    data: ScreenCreate,
) -> Screen:
    screen = Screen(**data.model_dump())

    db.add(screen)
    await db.commit()

    await db.refresh(screen)

    return screen


async def update_screen(
    db: AsyncSession,
    screen_id: uuid.UUID,
    data: ScreenUpdate,
) -> Screen:
    screen = await get_screen(db, screen_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(screen, field, value)

    await db.commit()
    await db.refresh(screen)

    return screen


async def delete_screen(
    db: AsyncSession,
    screen_id: uuid.UUID,
) -> None:
    screen = await get_screen(db, screen_id)

    await db.delete(screen)
    await db.commit()
