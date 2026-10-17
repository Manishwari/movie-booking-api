"""HTTP layer for the Theater slice.

Routers handle HTTP paths, status codes, and request/response models.
Business logic is delegated to the service layer.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, status

from movie_booking_api.api.deps import AdminUser, DbSession
from movie_booking_api.theaters import service
from movie_booking_api.theaters.models import Theater
from movie_booking_api.theaters.schemas import (
    TheaterCreate,
    TheaterRead,
    TheaterUpdate,
)

router = APIRouter(prefix="/theaters", tags=["theaters"])


@router.get("", response_model=list[TheaterRead])
async def list_theaters(
    db: DbSession,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Theater]:
    """List theaters. Public endpoint."""
    return await service.list_theaters(
        db,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=TheaterRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_theater(
    payload: TheaterCreate,
    db: DbSession,
    current_user: AdminUser,
) -> Theater:
    """Create a theater. Admin access required."""
    return await service.create_theater(db, payload)


@router.get("/{theater_id}", response_model=TheaterRead)
async def get_theater(
    theater_id: uuid.UUID,
    db: DbSession,
) -> Theater:
    """Get a theater by ID. Public endpoint."""
    return await service.get_theater(db, theater_id)


@router.patch("/{theater_id}", response_model=TheaterRead)
async def update_theater(
    theater_id: uuid.UUID,
    payload: TheaterUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> Theater:
    """Update a theater. Admin access required."""
    return await service.update_theater(
        db,
        theater_id,
        payload,
    )


@router.delete(
    "/{theater_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_theater(
    theater_id: uuid.UUID,
    db: DbSession,
    current_user: AdminUser,
) -> None:
    """Delete a theater. Admin access required."""
    await service.delete_theater(db, theater_id)
