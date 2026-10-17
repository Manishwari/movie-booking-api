"""Domain errors for the ``Movie`` slice.

These are plain exceptions with no HTTP vocabulary. ``main.py`` maps them onto
status codes, so the service layer can stay framework-free and unit-testable.
"""

from __future__ import annotations

import uuid


class MovieError(Exception):
    """Base class for movie domain errors."""


class MovieNotFoundError(MovieError):
    def __init__(self, movie_id: uuid.UUID) -> None:
        self.movie_id = movie_id
        super().__init__(f"Movie {movie_id} not found")
