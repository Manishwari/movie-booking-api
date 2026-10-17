"""HTTP layer for the Seat slice.

Routers handle HTTP paths, status codes, and request/response models.
Business logic is delegated to the service layer.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, status

from movie_booking_api.api.deps import AdminUser, DbSession
from movie_booking_api.seats.models import Seat
from movie_booking_api.seats.schemas import (
    SeatCreate,
    SeatRead,
    SeatUpdate,
)
from movie_booking_api.seats.service import (
    create_seat,
    delete_seat,
    get_seat,
    list_seats,
    update_seat,
)

router = APIRouter(
    prefix="/seats",
    tags=["seats"],
)


@router.get("", response_model=list[SeatRead])
async def list_seats_endpoint(
    db: DbSession,
) -> list[Seat]:
    """List seats. Public endpoint."""
    return list(await list_seats(db))


@router.post(
    "",
    response_model=SeatRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_seat_endpoint(
    data: SeatCreate,
    db: DbSession,
    current_user: AdminUser,
) -> Seat:
    """Create a seat. Admin access required."""
    return await create_seat(db, data)


@router.get("/{seat_id}", response_model=SeatRead)
async def get_seat_endpoint(
    seat_id: uuid.UUID,
    db: DbSession,
) -> Seat:
    """Get a seat by ID. Public endpoint."""
    return await get_seat(db, seat_id)


@router.patch("/{seat_id}", response_model=SeatRead)
async def update_seat_endpoint(
    seat_id: uuid.UUID,
    data: SeatUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> Seat:
    """Update a seat. Admin access required."""
    return await update_seat(db, seat_id, data)


@router.delete(
    "/{seat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_seat_endpoint(
    seat_id: uuid.UUID,
    db: DbSession,
    current_user: AdminUser,
) -> None:
    """Delete a seat. Admin access required."""
    await delete_seat(db, seat_id)
