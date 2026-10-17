"""HTTP layer for the Show slice.

Routers handle HTTP paths, status codes, and request/response models.
Business logic is delegated to the service layer.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, status

from movie_booking_api.api.deps import AdminUser, DbSession
from movie_booking_api.shows import service
from movie_booking_api.shows.models import Show
from movie_booking_api.shows.schemas import (
    ShowCreate,
    ShowRead,
    ShowUpdate,
)

router = APIRouter(prefix="/shows", tags=["shows"])


@router.get("", response_model=list[ShowRead])
async def list_shows(
    db: DbSession,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Show]:
    """List shows. Public endpoint."""
    return await service.list_shows(
        db,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=ShowRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_show(
    payload: ShowCreate,
    db: DbSession,
    current_user: AdminUser,
) -> Show:
    """Create a show. Admin access required."""
    return await service.create_show(db, payload)


@router.get("/{show_id}", response_model=ShowRead)
async def get_show(
    show_id: uuid.UUID,
    db: DbSession,
) -> Show:
    """Get a show by ID. Public endpoint."""
    return await service.get_show(db, show_id)


@router.patch("/{show_id}", response_model=ShowRead)
async def update_show(
    show_id: uuid.UUID,
    payload: ShowUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> Show:
    """Update a show. Admin access required."""
    return await service.update_show(
        db,
        show_id,
        payload,
    )


@router.delete(
    "/{show_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_show(
    show_id: uuid.UUID,
    db: DbSession,
    current_user: AdminUser,
) -> None:
    """Delete a show. Admin access required."""
    await service.delete_show(db, show_id)
