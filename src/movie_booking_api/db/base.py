"""Metadata aggregator -- the single module Alembic imports."""

from __future__ import annotations

from movie_booking_api.bookings.models import Booking as Booking
from movie_booking_api.bookings.models import BookingSeat as BookingSeat
from movie_booking_api.bookings.models import BookingStatus as BookingStatus
from movie_booking_api.db.base_class import Base as Base
from movie_booking_api.movies.models import Movie as Movie
from movie_booking_api.screens.models import Screen as Screen
from movie_booking_api.seats.models import Seat as Seat
from movie_booking_api.shows.models import Show as Show
from movie_booking_api.theaters.models import Theater as Theater
from movie_booking_api.users.models import User as User
from movie_booking_api.users.models import UserRole as UserRole

__all__ = [
    "Base",
    "Booking",
    "BookingSeat",
    "BookingStatus",
    "Movie",
    "Screen",
    "Seat",
    "Show",
    "Theater",
    "User",
    "UserRole",
]
