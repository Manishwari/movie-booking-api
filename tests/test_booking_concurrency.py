"""Concurrency tests for booking seat availability."""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from movie_booking_api.bookings.exceptions import SeatUnavailableError
from movie_booking_api.bookings.models import BookingSeat
from movie_booking_api.bookings.schemas import BookingCreate
from movie_booking_api.bookings.service import create_booking
from movie_booking_api.movies.models import Movie
from movie_booking_api.screens.models import Screen
from movie_booking_api.seats.models import Seat
from movie_booking_api.shows.models import Show
from movie_booking_api.theaters.models import Theater
from movie_booking_api.users.models import User, UserRole

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_concurrent_bookings_for_same_seat(
    engine: AsyncEngine,
) -> None:
    """Only one independent transaction can book a seat for a show."""

    # This test uses committed setup data because separate sessions
    # cannot see uncommitted rows from another transaction.
    async with AsyncSession(engine, expire_on_commit=False) as setup:
        user1 = User(
            email=f"concurrent-1-{uuid.uuid4().hex}@example.com",
            password_hash="test-password-hash",
            full_name="Concurrent Customer One",
            role=UserRole.CUSTOMER,
        )
        user2 = User(
            email=f"concurrent-2-{uuid.uuid4().hex}@example.com",
            password_hash="test-password-hash",
            full_name="Concurrent Customer Two",
            role=UserRole.CUSTOMER,
        )
        theater = Theater(name=f"Concurrency Theater {uuid.uuid4().hex}", location="Hyderabad")
        movie = Movie(name=f"Concurrency Movie {uuid.uuid4().hex}")

        setup.add_all([user1, user2, theater, movie])
        await setup.flush()

        screen = Screen(theater_id=theater.id, name="Concurrency Screen")
        setup.add(screen)
        await setup.flush()

        show = Show(
            movie_id=movie.id,
            screen_id=screen.id,
            start_time=datetime.now(UTC) + timedelta(hours=1),
            end_time=datetime.now(UTC) + timedelta(hours=3),
            ticket_price=Decimal("250.00"),
        )
        seat = Seat(screen_id=screen.id, seat_number="A1")
        setup.add_all([show, seat])
        await setup.commit()

        user1_id = user1.id
        user2_id = user2.id
        show_id = show.id
        seat_id = seat.id

    # Each attempt uses its own session and transaction.
    start = asyncio.Event()

    async def attempt_booking(user_id: uuid.UUID) -> str:
        async with AsyncSession(engine, expire_on_commit=False) as db:
            await start.wait()
            try:
                await create_booking(
                    db,
                    user_id,
                    BookingCreate(show_id=show_id, seat_ids=[seat_id]),
                )
                return "success"
            except SeatUnavailableError:
                return "unavailable"

    try:
        first_task = asyncio.create_task(attempt_booking(user1_id))
        second_task = asyncio.create_task(attempt_booking(user2_id))

        start.set()
        results = await asyncio.gather(first_task, second_task)

        assert results.count("success") == 1
        assert results.count("unavailable") == 1

        async with AsyncSession(engine) as verify:
            result = await verify.execute(
                select(BookingSeat).where(
                    BookingSeat.show_id == show_id,
                    BookingSeat.seat_id == seat_id,
                )
            )
            assert len(list(result.scalars().all())) == 1
    finally:
        # Remove committed test data in dependency order.
        async with AsyncSession(engine) as cleanup:
            from sqlalchemy import delete

            await cleanup.execute(delete(BookingSeat).where(BookingSeat.show_id == show_id))
            from movie_booking_api.bookings.models import Booking

            await cleanup.execute(delete(Booking).where(Booking.show_id == show_id))
            await cleanup.execute(delete(Show).where(Show.id == show_id))
            await cleanup.execute(delete(Seat).where(Seat.id == seat_id))
            await cleanup.execute(delete(Screen).where(Screen.id == screen.id))
            await cleanup.execute(delete(Movie).where(Movie.id == movie.id))
            await cleanup.execute(delete(Theater).where(Theater.id == theater.id))
            await cleanup.execute(delete(User).where(User.id.in_([user1_id, user2_id])))
            await cleanup.commit()
