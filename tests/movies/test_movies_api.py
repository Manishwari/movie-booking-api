"""End-to-end tests for the Movie slice.

Reference for testing your own features: drive the API through ``client`` and
assert against the same ``session`` the request used.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.core.security import create_access_token
from movie_booking_api.movies import service
from movie_booking_api.movies.exceptions import MovieNotFoundError
from movie_booking_api.movies.schemas import MovieCreate
from movie_booking_api.users.models import User, UserRole

pytestmark = pytest.mark.integration


async def create_admin_user(session: AsyncSession) -> User:
    """Create an admin user for movie management tests."""

    admin = User(
        email=f"admin-{uuid.uuid4().hex}@example.com",
        password_hash="test-password-hash",
        full_name="Test Admin",
        role=UserRole.ADMIN,
    )
    session.add(admin)
    await session.flush()
    return admin


def admin_headers(admin: User) -> dict[str, str]:
    """Return authentication headers for an admin user."""

    token = create_access_token(str(admin.id))
    return {"Authorization": f"Bearer {token}"}


async def test_create_and_read_movie(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    admin = await create_admin_user(session)

    create = await client.post(
        "/api/v1/movies",
        json={"name": "widget", "description": "a test widget"},
        headers=admin_headers(admin),
    )
    assert create.status_code == 201

    created = create.json()
    assert created["name"] == "widget"
    assert created["id"]
    assert created["created_at"]

    fetched = await client.get(f"/api/v1/movies/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == created


async def test_list_movies(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    admin = await create_admin_user(session)
    headers = admin_headers(admin)

    for name in ("alpha", "beta"):
        response = await client.post(
            "/api/v1/movies",
            json={"name": name},
            headers=headers,
        )
        assert response.status_code == 201

    listed = await client.get("/api/v1/movies")
    assert listed.status_code == 200

    names = {movie["name"] for movie in listed.json()}
    assert {"alpha", "beta"} <= names


async def test_update_movie(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    admin = await create_admin_user(session)
    headers = admin_headers(admin)

    create_response = await client.post(
        "/api/v1/movies",
        json={"name": "before"},
        headers=headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()

    updated = await client.patch(
        f"/api/v1/movies/{created['id']}",
        json={"name": "after"},
        headers=headers,
    )

    assert updated.status_code == 200
    assert updated.json()["name"] == "after"
    assert updated.json()["description"] == created["description"]


async def test_delete_movie(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    admin = await create_admin_user(session)
    headers = admin_headers(admin)

    create_response = await client.post(
        "/api/v1/movies",
        json={"name": "doomed"},
        headers=headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()

    deleted = await client.delete(
        f"/api/v1/movies/{created['id']}",
        headers=headers,
    )
    assert deleted.status_code == 204

    missing = await client.get(f"/api/v1/movies/{created['id']}")
    assert missing.status_code == 404


async def test_unknown_movie_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/movies/{uuid.uuid4()}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_validation_rejects_empty_name(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    admin = await create_admin_user(session)

    response = await client.post(
        "/api/v1/movies",
        json={"name": ""},
        headers=admin_headers(admin),
    )

    assert response.status_code == 422


async def test_service_raises_domain_error(session: AsyncSession) -> None:
    """The service layer is a plain callable -- no app, no request needed."""

    movie = await service.create_movie(session, MovieCreate(name="direct"))
    assert movie.name == "direct"

    await service.delete_movie(session, movie.id)

    with pytest.raises(MovieNotFoundError):
        await service.get_movie(session, movie.id)
