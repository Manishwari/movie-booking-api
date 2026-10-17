"""HTTP layer for the Movie slice.

Routers handle HTTP paths, status codes, and request/response models.
Business logic is delegated to the service layer.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, status

from movie_booking_api.api.deps import AdminUser, DbSession
from movie_booking_api.movies import service
from movie_booking_api.movies.models import Movie
from movie_booking_api.movies.schemas import MovieCreate, MovieRead, MovieUpdate

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=list[MovieRead])
async def list_movies(
    db: DbSession,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Movie]:
    """List movies. This endpoint is public."""
    return await service.list_movies(
        db,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_movie(
    payload: MovieCreate,
    db: DbSession,
    current_user: AdminUser,
) -> Movie:
    """Create a movie. Admin access is required."""
    return await service.create_movie(db, payload)


@router.get("/{movie_id}", response_model=MovieRead)
async def get_movie(
    movie_id: uuid.UUID,
    db: DbSession,
) -> Movie:
    """Get a movie by ID. This endpoint is public."""
    return await service.get_movie(db, movie_id)


@router.patch("/{movie_id}", response_model=MovieRead)
async def update_movie(
    movie_id: uuid.UUID,
    payload: MovieUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> Movie:
    """Update a movie. Admin access is required."""
    return await service.update_movie(
        db,
        movie_id,
        payload,
    )


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_movie(
    movie_id: uuid.UUID,
    db: DbSession,
    current_user: AdminUser,
) -> None:
    """Delete a movie. Admin access is required."""
    await service.delete_movie(db, movie_id)
