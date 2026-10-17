"""Business logic for the ``Movie`` slice.

This module owns the transaction boundary and knows nothing about HTTP. It
imports no FastAPI -- and Ruff enforces that (see the ``banned-api`` section in
pyproject.toml), so the rule cannot quietly rot.

The session is passed in explicitly rather than resolved from a dependency,
which keeps these functions ordinary callables you can test with no app and no
request.

Note there is no repository layer. ``AsyncSession`` is already a Unit of Work
plus Data Mapper; a class wrapping ``session.execute(select(Movie))`` would add
indirection and buy nothing. Introduce one only when you have a second
persistence backend, or logic complex enough to test with no database at all.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.movies.exceptions import MovieNotFoundError
from movie_booking_api.movies.models import Movie
from movie_booking_api.movies.schemas import MovieCreate, MovieUpdate


async def list_movies(db: AsyncSession, *, limit: int = 50, offset: int = 0) -> Sequence[Movie]:
    stmt = select(Movie).order_by(Movie.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_movie(db: AsyncSession, movie_id: uuid.UUID) -> Movie:
    movie = await db.get(Movie, movie_id)
    if movie is None:
        raise MovieNotFoundError(movie_id)
    return movie


async def create_movie(db: AsyncSession, data: MovieCreate) -> Movie:
    movie = Movie(**data.model_dump())
    db.add(movie)
    await db.commit()

    # refresh() pulls server-generated columns (id, created_at) back from the DB.
    await db.refresh(movie)
    return movie


async def update_movie(db: AsyncSession, movie_id: uuid.UUID, data: MovieUpdate) -> Movie:
    movie = await get_movie(db, movie_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)

    await db.commit()
    await db.refresh(movie)
    return movie


async def delete_movie(db: AsyncSession, movie_id: uuid.UUID) -> None:
    movie = await get_movie(db, movie_id)
    await db.delete(movie)
    await db.commit()
