"""API routes for movie ticket bookings."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.api.deps import CurrentUser
from movie_booking_api.bookings.models import Booking, BookingSeat
from movie_booking_api.bookings.schemas import (
    BookingCancelResponse,
    BookingCreate,
    BookingRead,
)
from movie_booking_api.bookings.service import (
    cancel_booking,
    create_booking,
    get_booking,
    list_my_bookings,
)
from movie_booking_api.db.session import get_db

router = APIRouter(prefix="/bookings", tags=["Bookings"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def to_booking_read(
    db: AsyncSession,
    booking: Booking,
) -> BookingRead:
    """Convert a booking and its seat records into a response schema."""

    result = await db.execute(
        select(BookingSeat.seat_id).where(BookingSeat.booking_id == booking.id)
    )
    seat_ids = list(result.scalars().all())

    return BookingRead(
        id=booking.id,
        user_id=booking.user_id,
        show_id=booking.show_id,
        status=booking.status,
        total_amount=booking.total_amount,
        created_at=booking.created_at,
        seat_ids=seat_ids,
    )


@router.post(
    "/",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking_endpoint(
    data: BookingCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> BookingRead:
    """Book seats for a show."""

    booking = await create_booking(db, current_user.id, data)
    return await to_booking_read(db, booking)


@router.get("/", response_model=list[BookingRead])
async def list_my_bookings_endpoint(
    current_user: CurrentUser,
    db: DbSession,
) -> list[BookingRead]:
    """List the current user's bookings."""

    bookings = await list_my_bookings(db, current_user.id)
    return [await to_booking_read(db, booking) for booking in bookings]


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking_endpoint(
    booking_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> BookingRead:
    """Get one of the current user's bookings."""

    booking = await get_booking(db, booking_id, current_user.id)
    return await to_booking_read(db, booking)


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingCancelResponse,
)
async def cancel_booking_endpoint(
    booking_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> BookingCancelResponse:
    """Cancel one of the current user's bookings."""

    booking = await cancel_booking(db, booking_id, current_user.id)
    return BookingCancelResponse(
        id=booking.id,
        status=booking.status,
    )
