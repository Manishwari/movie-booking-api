"""Integration tests for the movie booking API."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.core.security import create_access_token
from movie_booking_api.movies.models import Movie
from movie_booking_api.screens.models import Screen
from movie_booking_api.seats.models import Seat
from movie_booking_api.shows.models import Show
from movie_booking_api.theaters.models import Theater
from movie_booking_api.users.models import User, UserRole

pytestmark = pytest.mark.integration


async def create_booking_test_data(
    session: AsyncSession,
) -> tuple[User, Show, Seat]:
    """Create a customer, show, and seat for booking tests."""

    user = User(
        email=f"booking-{uuid.uuid4().hex}@example.com",
        password_hash="test-password-hash",
        full_name="Booking Test Customer",
        role=UserRole.CUSTOMER,
    )
    theater = Theater(
        name="Test Theater",
        location="Hyderabad",
    )
    movie = Movie(name="Test Movie")

    session.add_all([user, theater, movie])
    await session.flush()

    screen = Screen(
        theater_id=theater.id,
        name="Screen 1",
    )
    session.add(screen)
    await session.flush()

    now = datetime.now(UTC)
    show = Show(
        movie_id=movie.id,
        screen_id=screen.id,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        ticket_price=Decimal("250.00"),
    )
    seat = Seat(
        screen_id=screen.id,
        seat_number="A1",
    )
    session.add_all([show, seat])
    await session.flush()

    return user, show, seat


def auth_headers(user: User) -> dict[str, str]:
    """Return authentication headers for a test customer."""

    token = create_access_token(str(user.id))
    return {"Authorization": f"Bearer {token}"}


def booking_payload(show: Show, seat: Seat) -> dict[str, object]:
    """Build the request payload for a single-seat booking."""

    return {
        "show_id": str(show.id),
        "seat_ids": [str(seat.id)],
    }


@pytest.mark.asyncio
async def test_create_booking_requires_authentication(
    anon_client: AsyncClient,
) -> None:
    """Creating a booking without a token should return 401."""

    response = await anon_client.post(
        "/api/v1/bookings/",
        json={
            "show_id": str(uuid.uuid4()),
            "seat_ids": [str(uuid.uuid4())],
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_booking_as_customer(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """An authenticated customer can book an available seat."""

    user, show, seat = await create_booking_test_data(session)

    response = await client.post(
        "/api/v1/bookings/",
        headers=auth_headers(user),
        json=booking_payload(show, seat),
    )

    assert response.status_code == 201

    body = response.json()
    assert body["user_id"] == str(user.id)
    assert body["show_id"] == str(show.id)
    assert body["status"] == "CONFIRMED"
    assert Decimal(body["total_amount"]) == Decimal("250.00")
    assert body["seat_ids"] == [str(seat.id)]
    assert body["id"]
    assert body["created_at"]


@pytest.mark.asyncio
async def test_cannot_book_the_same_seat_twice(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """A seat already booked for a show cannot be booked again."""

    user, show, seat = await create_booking_test_data(session)
    headers = auth_headers(user)
    payload = booking_payload(show, seat)

    first = await client.post(
        "/api/v1/bookings/",
        headers=headers,
        json=payload,
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/bookings/",
        headers=headers,
        json=payload,
    )
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_cancel_booking_releases_seat(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Cancelling a booking releases its seat for another booking."""

    user, show, seat = await create_booking_test_data(session)
    headers = auth_headers(user)

    booking_response = await client.post(
        "/api/v1/bookings/",
        headers=headers,
        json=booking_payload(show, seat),
    )
    assert booking_response.status_code == 201
    booking_id = booking_response.json()["id"]

    cancel_response = await client.post(
        f"/api/v1/bookings/{booking_id}/cancel",
        headers=headers,
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["id"] == booking_id
    assert cancel_response.json()["status"] == "CANCELLED"

    rebooking_response = await client.post(
        "/api/v1/bookings/",
        headers=headers,
        json=booking_payload(show, seat),
    )

    assert rebooking_response.status_code == 201


@pytest.mark.asyncio
async def test_customer_cannot_view_another_customers_booking(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """A customer cannot view another customer's booking."""

    owner, show, seat = await create_booking_test_data(session)
    other_customer = User(
        email=f"other-{uuid.uuid4().hex}@example.com",
        password_hash="test-password-hash",
        full_name="Another Customer",
        role=UserRole.CUSTOMER,
    )
    session.add(other_customer)
    await session.flush()

    booking_response = await client.post(
        "/api/v1/bookings/",
        headers=auth_headers(owner),
        json=booking_payload(show, seat),
    )
    assert booking_response.status_code == 201

    booking_id = booking_response.json()["id"]
    response = await client.get(
        f"/api/v1/bookings/{booking_id}",
        headers=auth_headers(other_customer),
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_customer_cannot_cancel_another_customers_booking(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """A customer cannot cancel another customer's booking."""

    owner, show, seat = await create_booking_test_data(session)
    other_customer = User(
        email=f"other-{uuid.uuid4().hex}@example.com",
        password_hash="test-password-hash",
        full_name="Another Customer",
        role=UserRole.CUSTOMER,
    )
    session.add(other_customer)
    await session.flush()

    booking_response = await client.post(
        "/api/v1/bookings/",
        headers=auth_headers(owner),
        json=booking_payload(show, seat),
    )
    assert booking_response.status_code == 201

    booking_id = booking_response.json()["id"]
    response = await client.post(
        f"/api/v1/bookings/{booking_id}/cancel",
        headers=auth_headers(other_customer),
    )

    assert response.status_code == 403

    owner_response = await client.get(
        f"/api/v1/bookings/{booking_id}",
        headers=auth_headers(owner),
    )
    assert owner_response.status_code == 200
    assert owner_response.json()["status"] == "CONFIRMED"


@pytest.mark.asyncio
async def test_customer_can_list_own_bookings(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """A customer can list their own bookings."""

    user, show, seat = await create_booking_test_data(session)

    booking_response = await client.post(
        "/api/v1/bookings/",
        headers=auth_headers(user),
        json=booking_payload(show, seat),
    )
    assert booking_response.status_code == 201

    response = await client.get(
        "/api/v1/bookings/",
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == booking_response.json()["id"]
    assert body[0]["user_id"] == str(user.id)


@pytest.mark.asyncio
async def test_booking_rejects_unknown_seat(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """Booking a nonexistent seat should return 422."""

    user, show, _ = await create_booking_test_data(session)

    response = await client.post(
        "/api/v1/bookings/",
        headers=auth_headers(user),
        json={
            "show_id": str(show.id),
            "seat_ids": [str(uuid.uuid4())],
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_booking_rejects_duplicate_seat_ids(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    """The same seat cannot appear twice in one booking request."""

    user, show, seat = await create_booking_test_data(session)

    response = await client.post(
        "/api/v1/bookings/",
        headers=auth_headers(user),
        json={
            "show_id": str(show.id),
            "seat_ids": [str(seat.id), str(seat.id)],
        },
    )

    assert response.status_code == 422
