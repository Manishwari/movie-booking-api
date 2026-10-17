"""Aggregates every feature router under the versioned API prefix.

Adding a feature slice is one import and one ``include_router`` line here.
"""

from __future__ import annotations

from fastapi import APIRouter

from movie_booking_api.bookings.router import router as bookings_router
from movie_booking_api.movies.router import router as movies_router
from movie_booking_api.screens.router import router as screens_router
from movie_booking_api.seats.router import router as seats_router
from movie_booking_api.shows.router import router as shows_router
from movie_booking_api.theaters.router import router as theaters_router
from movie_booking_api.users.router import router as users_router

api_router = APIRouter()

api_router.include_router(movies_router)
api_router.include_router(theaters_router)
api_router.include_router(screens_router)
api_router.include_router(seats_router)
api_router.include_router(shows_router)
api_router.include_router(users_router)
api_router.include_router(bookings_router)
