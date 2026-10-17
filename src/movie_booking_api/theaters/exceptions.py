import uuid


class TheaterError(Exception):
    """Base exception for theater-related errors."""


class TheaterNotFoundError(TheaterError):
    def __init__(self, theater_id: uuid.UUID) -> None:
        self.theater_id = theater_id
        super().__init__(f"Theater {theater_id} not found")
