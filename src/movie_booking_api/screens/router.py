"""HTTP layer for the Screen slice.

Routers handle HTTP paths, status codes, and request/response models.
Business logic is delegated to the service layer.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, status

from movie_booking_api.api.deps import AdminUser, DbSession
from movie_booking_api.screens import service
from movie_booking_api.screens.models import Screen
from movie_booking_api.screens.schemas import (
    ScreenCreate,
    ScreenRead,
    ScreenUpdate,
)

router = APIRouter(prefix="/screens", tags=["screens"])


@router.get("", response_model=list[ScreenRead])
async def list_screens(
    db: DbSession,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Screen]:
    """List screens. Public endpoint."""
    return await service.list_screens(
        db,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=ScreenRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_screen(
    payload: ScreenCreate,
    db: DbSession,
    current_user: AdminUser,
) -> Screen:
    """Create a screen. Admin access required."""
    return await service.create_screen(db, payload)


@router.get("/{screen_id}", response_model=ScreenRead)
async def get_screen(
    screen_id: uuid.UUID,
    db: DbSession,
) -> Screen:
    """Get a screen by ID. Public endpoint."""
    return await service.get_screen(db, screen_id)


@router.patch("/{screen_id}", response_model=ScreenRead)
async def update_screen(
    screen_id: uuid.UUID,
    payload: ScreenUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> Screen:
    """Update a screen. Admin access required."""
    return await service.update_screen(
        db,
        screen_id,
        payload,
    )


@router.delete(
    "/{screen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_screen(
    screen_id: uuid.UUID,
    db: DbSession,
    current_user: AdminUser,
) -> None:
    """Delete a screen. Admin access required."""
    await service.delete_screen(db, screen_id)
