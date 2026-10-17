from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.db.session import AsyncSessionLocal
from movie_booking_api.movies.models import Movie
from movie_booking_api.screens.models import Screen
from movie_booking_api.seats.models import Seat
from movie_booking_api.shows.models import Show
from movie_booking_api.theaters.models import Theater
from movie_booking_api.users.models import User, UserRole

password_hash = PasswordHash.recommended()


# ---------------------------------------------------------
# USERS
# ---------------------------------------------------------

USERS = [
    {
        "email": "admin@gmail.com",
        "password": "Admin@123",
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
    },
    {
        "email": "owner@gmail.com",
        "password": "Owner@123",
        "full_name": "Theater Owner",
        "role": UserRole.THEATER_OWNER,
    },
]


# ---------------------------------------------------------
# MOVIES
# ---------------------------------------------------------

MOVIES = [
    {
        "name": "Interstellar",
        "description": "A science fiction movie about space, time, and humanity.",
    },
    {
        "name": "Inception",
        "description": "A thief enters people's dreams to steal and plant ideas.",
    },
    {
        "name": "The Dark Knight",
        "description": "A superhero movie about a dangerous criminal mastermind.",
    },
    {
        "name": "Avengers: Endgame",
        "description": "The Avengers attempt to undo a devastating event.",
    },
    {
        "name": "Dune: Part Two",
        "description": "Paul Atreides joins the Fremen on a journey of revenge.",
    },
]


# ---------------------------------------------------------
# THEATERS
# ---------------------------------------------------------

THEATERS = [
    {
        "name": "PVR Cinemas",
        "location": "Banjara Hills, Hyderabad",
    },
    {
        "name": "AMB Cinemas",
        "location": "Gachibowli, Hyderabad",
    },
    {
        "name": "Prasads Multiplex",
        "location": "NTR Marg, Hyderabad",
    },
]


# ---------------------------------------------------------
# SEATS
#
# 5 rows x 10 seats = 50 seats per screen
#
# A1 A2 A3 ... A10
# B1 B2 B3 ... B10
# C1 C2 C3 ... C10
# D1 D2 D3 ... D10
# E1 E2 E3 ... E10
#
# 9 screens x 50 seats = 450 seats
# ---------------------------------------------------------

SEAT_ROWS = ["A", "B", "C", "D", "E"]
SEATS_PER_ROW = 10


# ---------------------------------------------------------
# SHOW TIMES
#
# 3 shows per screen
# ---------------------------------------------------------

SHOW_TIMES = [
    (10, 0),
    (14, 0),
    (19, 0),
]


# ---------------------------------------------------------
# SEED USERS
# ---------------------------------------------------------


async def seed_users(db: AsyncSession) -> list[User]:
    users: list[User] = []

    for user_data in USERS:
        result = await db.execute(select(User).where(User.email == user_data["email"]))

        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                email=user_data["email"],
                password_hash=password_hash.hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
            )
            db.add(user)

        users.append(user)

    await db.flush()

    return users


# ---------------------------------------------------------
# SEED MOVIES
# ---------------------------------------------------------


async def seed_movies(db: AsyncSession) -> list[Movie]:
    movies: list[Movie] = []

    for movie_data in MOVIES:
        result = await db.execute(select(Movie).where(Movie.name == movie_data["name"]))

        movie = result.scalar_one_or_none()

        if movie is None:
            movie = Movie(**movie_data)
            db.add(movie)

        movies.append(movie)

    await db.flush()

    return movies


# ---------------------------------------------------------
# SEED THEATERS
# ---------------------------------------------------------


async def seed_theaters(db: AsyncSession) -> list[Theater]:
    theaters: list[Theater] = []

    for theater_data in THEATERS:
        result = await db.execute(
            select(Theater).where(
                Theater.name == theater_data["name"],
                Theater.location == theater_data["location"],
            )
        )

        theater = result.scalar_one_or_none()

        if theater is None:
            theater = Theater(**theater_data)
            db.add(theater)

        theaters.append(theater)

    await db.flush()

    return theaters


# ---------------------------------------------------------
# SEED SCREENS
#
# 3 screens per theater
#
# 3 theaters x 3 screens = 9 screens
# ---------------------------------------------------------


async def seed_screens(
    db: AsyncSession,
    theaters: list[Theater],
) -> list[Screen]:
    screens: list[Screen] = []

    for theater in theaters:
        for screen_number in range(1, 4):
            screen_name = f"Screen {screen_number}"

            result = await db.execute(
                select(Screen).where(
                    Screen.theater_id == theater.id,
                    Screen.name == screen_name,
                )
            )

            screen = result.scalar_one_or_none()

            if screen is None:
                screen = Screen(
                    theater_id=theater.id,
                    name=screen_name,
                )
                db.add(screen)

            screens.append(screen)

    await db.flush()

    return screens


# ---------------------------------------------------------
# SEED SEATS
#
# 50 seats per screen
# 9 screens x 50 seats = 450 seats
#
# IMPORTANT:
# Seats belong to a SCREEN, not to a SHOW.
# ---------------------------------------------------------


async def seed_seats(
    db: AsyncSession,
    screens: list[Screen],
) -> list[Seat]:
    seats: list[Seat] = []

    for screen in screens:
        for row in SEAT_ROWS:
            for seat_number in range(1, SEATS_PER_ROW + 1):
                seat_name = f"{row}{seat_number}"

                result = await db.execute(
                    select(Seat).where(
                        Seat.screen_id == screen.id,
                        Seat.seat_number == seat_name,
                    )
                )

                seat = result.scalar_one_or_none()

                if seat is None:
                    seat = Seat(
                        screen_id=screen.id,
                        seat_number=seat_name,
                    )
                    db.add(seat)

                seats.append(seat)

    await db.flush()

    return seats


# ---------------------------------------------------------
# SEED SHOWS
#
# 3 shows per screen
# 9 screens x 3 shows = 27 shows
#
# The seats belong to the SCREEN, not the SHOW.
#
# Example:
#
# Screen 1
#   ├── Interstellar 10:00
#   ├── Inception    14:00
#   └── Dune         19:00
#
# All three shows use the same 50 physical seats.
# ---------------------------------------------------------


async def seed_shows(
    db: AsyncSession,
    movies: list[Movie],
    screens: list[Screen],
) -> list[Show]:
    shows: list[Show] = []

    # Fixed date makes the seed repeatable.
    base_date = datetime(
        2026,
        9,
        10,
        tzinfo=UTC,
    )

    for screen_index, screen in enumerate(screens):
        for show_index, (hour, minute) in enumerate(SHOW_TIMES):
            # Rotate movies between screens and show times.
            movie = movies[(screen_index + show_index) % len(movies)]

            # Each theater gets its own day.
            theater_day = screen_index // 3

            start_time = base_date + timedelta(
                days=theater_day,
                hours=hour,
                minutes=minute,
            )

            end_time = start_time + timedelta(
                hours=2,
                minutes=30,
            )

            # Check whether this exact show already exists.
            result = await db.execute(
                select(Show).where(
                    Show.screen_id == screen.id,
                    Show.movie_id == movie.id,
                    Show.start_time == start_time,
                )
            )

            show = result.scalar_one_or_none()

            if show is None:
                show = Show(
                    movie_id=movie.id,
                    screen_id=screen.id,
                    start_time=start_time,
                    end_time=end_time,
                    ticket_price=Decimal("250.00"),
                )
                db.add(show)

            shows.append(show)

    await db.flush()

    return shows


# ---------------------------------------------------------
# MAIN SEED FUNCTION
# ---------------------------------------------------------


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        try:
            users = await seed_users(db)

            movies = await seed_movies(db)

            theaters = await seed_theaters(db)

            screens = await seed_screens(
                db,
                theaters,
            )

            seats = await seed_seats(
                db,
                screens,
            )

            shows = await seed_shows(
                db,
                movies,
                screens,
            )

            await db.commit()

            print()
            print("Database seeded successfully!")
            print("--------------------------------")
            print(f"Users:    {len(users)}")
            print(f"Movies:   {len(movies)}")
            print(f"Theaters: {len(theaters)}")
            print(f"Screens:  {len(screens)}")
            print(f"Shows:    {len(shows)}")
            print(f"Seats:    {len(seats)}")
            print("--------------------------------")
            print("Expected:")
            print("2 users")
            print("5 movies")
            print("3 theaters")
            print("9 screens")
            print("27 shows")
            print("450 seats")
            print("--------------------------------")

        except Exception:
            await db.rollback()
            raise


# ---------------------------------------------------------
# RUN SCRIPT
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(seed())
