"""Business logic for the bookings slice."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.bookings.exceptions import (
    BookingNotFoundError,
    BookingPermissionError,
    InvalidSeatSelectionError,
    SeatUnavailableError,
    ShowNotFoundError,
)
from movie_booking_api.bookings.models import Booking, BookingSeat, BookingStatus
from movie_booking_api.bookings.schemas import BookingCreate
from movie_booking_api.seats.models import Seat
from movie_booking_api.shows.models import Show


async def create_booking(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: BookingCreate,
) -> Booking:
    """Book seats for a show and calculate the total amount."""

    if len(data.seat_ids) != len(set(data.seat_ids)):
        raise InvalidSeatSelectionError("Duplicate seat IDs were provided.")

    try:
        # Lock the show row before checking seat availability.
        # PostgreSQL makes competing booking transactions wait here.
        show_result = await db.execute(
            select(Show).where(Show.id == data.show_id).with_for_update()
        )
        show = show_result.scalar_one_or_none()

        if show is None:
            raise ShowNotFoundError(data.show_id)

        # Validate that every requested seat exists.
        seats_result = await db.execute(select(Seat).where(Seat.id.in_(data.seat_ids)))
        seats = list(seats_result.scalars().all())

        if len(seats) != len(data.seat_ids):
            found_ids = {seat.id for seat in seats}
            missing_ids = [seat_id for seat_id in data.seat_ids if seat_id not in found_ids]
            raise InvalidSeatSelectionError(f"Unknown seat IDs: {missing_ids}")

        # All seats must belong to the screen hosting this show.
        if any(seat.screen_id != show.screen_id for seat in seats):
            raise InvalidSeatSelectionError("Every selected seat must belong to the show's screen.")

        # Check whether any requested seats are already booked.
        booked_result = await db.execute(
            select(BookingSeat.seat_id).where(
                BookingSeat.show_id == data.show_id,
                BookingSeat.seat_id.in_(data.seat_ids),
            )
        )
        booked_seat_ids = list(booked_result.scalars().all())

        if booked_seat_ids:
            raise SeatUnavailableError(booked_seat_ids)

        total_amount = Decimal(str(show.ticket_price)) * len(data.seat_ids)

        booking = Booking(
            user_id=user_id,
            show_id=data.show_id,
            total_amount=total_amount,
            status=BookingStatus.CONFIRMED,
        )
        db.add(booking)

        # Generate the booking ID before creating its seat records.
        await db.flush()

        for seat_id in data.seat_ids:
            db.add(
                BookingSeat(
                    booking_id=booking.id,
                    show_id=data.show_id,
                    seat_id=seat_id,
                )
            )

        await db.commit()
        await db.refresh(booking)

    except IntegrityError as exc:
        await db.rollback()
        raise SeatUnavailableError(data.seat_ids) from exc
    except Exception:
        await db.rollback()
        raise

    return booking


async def list_my_bookings(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[Booking]:
    """Return bookings belonging to one user."""

    result = await db.execute(
        select(Booking).where(Booking.user_id == user_id).order_by(Booking.created_at.desc())
    )
    return list(result.scalars().all())


async def get_booking(
    db: AsyncSession,
    booking_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Booking:
    """Get a booking belonging to the current user."""

    booking = await db.get(Booking, booking_id)

    if booking is None:
        raise BookingNotFoundError(booking_id)

    if booking.user_id != user_id:
        raise BookingPermissionError("You cannot access another user's booking.")

    return booking


async def cancel_booking(
    db: AsyncSession,
    booking_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Booking:
    """Cancel a user's booking and release its seats."""

    booking = await db.get(Booking, booking_id)

    if booking is None:
        raise BookingNotFoundError(booking_id)

    if booking.user_id != user_id:
        raise BookingPermissionError("You cannot cancel another user's booking.")

    if booking.status == BookingStatus.CANCELLED:
        return booking

    try:
        # Lock the booking before changing its status or releasing seats.
        await db.execute(select(Booking.id).where(Booking.id == booking_id).with_for_update())

        booking.status = BookingStatus.CANCELLED

        seat_result = await db.execute(
            select(BookingSeat).where(BookingSeat.booking_id == booking_id)
        )
        booking_seats = list(seat_result.scalars().all())

        for booking_seat in booking_seats:
            await db.delete(booking_seat)

        await db.commit()
        await db.refresh(booking)
    except Exception:
        await db.rollback()
        raise

    return booking
