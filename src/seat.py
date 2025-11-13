from __future__ import annotations
from typing import Optional

from player import Player


class Seat:
    """
    Represents a single seat at a blackjack table.
    Each seat holds one player or remains empty (None).
    """

    def __init__(self, seat_index: int) -> None:
        """
        Initialize a seat with a given index.

        Args:
            seat_index (int): The position number of the seat at the table.
        """
        self.seat_index: int = seat_index
        self.player: Optional[Player] = None
