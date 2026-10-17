"""Application entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from movie_booking_api.api.health import router as health_router
from movie_booking_api.api.router import api_router
from movie_booking_api.bookings.exceptions import (
    BookingNotFoundError,
    BookingPermissionError,
    InvalidSeatSelectionError,
    SeatNotFoundError,
    SeatUnavailableError,
    ShowNotFoundError,
)
from movie_booking_api.core.config import get_settings
from movie_booking_api.core.logging import configure_logging
from movie_booking_api.db.session import engine
from movie_booking_api.movies.exceptions import MovieNotFoundError
from movie_booking_api.screens.exceptions import ScreenNotFoundError
from movie_booking_api.users.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configure application startup and shutdown."""

    configure_logging(debug=settings.debug)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="A FastAPI service for movie ticket booking backed by PostgreSQL.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)


@app.exception_handler(MovieNotFoundError)
async def movie_not_found_handler(
    request: Request,
    exc: MovieNotFoundError,
) -> JSONResponse:
    """Map a missing movie to HTTP 404."""

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(ScreenNotFoundError)
async def screen_not_found_handler(
    request: Request,
    exc: ScreenNotFoundError,
) -> JSONResponse:
    """Map a missing screen to HTTP 404."""

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(
    request: Request,
    exc: UserAlreadyExistsError,
) -> JSONResponse:
    """Map a duplicate user to HTTP 409."""

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(
    request: Request,
    exc: InvalidCredentialsError,
) -> JSONResponse:
    """Map invalid credentials to HTTP 401."""

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ShowNotFoundError)
async def show_not_found_handler(
    request: Request,
    exc: ShowNotFoundError,
) -> JSONResponse:
    """Map a missing show to HTTP 404."""

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(SeatNotFoundError)
async def seat_not_found_handler(
    request: Request,
    exc: SeatNotFoundError,
) -> JSONResponse:
    """Map a missing seat to HTTP 404."""

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(BookingNotFoundError)
async def booking_not_found_handler(
    request: Request,
    exc: BookingNotFoundError,
) -> JSONResponse:
    """Map a missing booking to HTTP 404."""

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(BookingPermissionError)
async def booking_permission_handler(
    request: Request,
    exc: BookingPermissionError,
) -> JSONResponse:
    """Map booking permission errors to HTTP 403."""

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)},
    )


@app.exception_handler(SeatUnavailableError)
async def seat_unavailable_handler(
    request: Request,
    exc: SeatUnavailableError,
) -> JSONResponse:
    """Map unavailable seats to HTTP 409."""

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidSeatSelectionError)
async def invalid_seat_selection_handler(
    request: Request,
    exc: InvalidSeatSelectionError,
) -> JSONResponse:
    """Map an invalid seat selection to HTTP 422."""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Return basic application information."""

    return {
        "name": settings.app_name,
        "environment": settings.environment,
        "docs": "/docs",
    }


app.include_router(health_router)
app.include_router(api_router, prefix=settings.api_v1_prefix)
