import uuid


class ShowError(Exception):
    """Base exception for show-related errors."""


class ShowNotFoundError(ShowError):
    def __init__(self, show_id: uuid.UUID) -> None:
        self.show_id = show_id
        super().__init__(f"Show {show_id} not found")
