import uuid


class SeatError(Exception):
    """Base exception for seat-related errors."""


class SeatNotFoundError(SeatError):
    def __init__(self, seat_id: uuid.UUID) -> None:
        self.seat_id = seat_id
        super().__init__(f"Seat {seat_id} not found")
