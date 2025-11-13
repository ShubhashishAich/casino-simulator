"""
casino.py - Defines the Casino class, which manages all blackjack tables and global casino statistics.

Attributes:
    casino_name (str) - Name of the casino.
    tables (List[Table]) - Collection of all active tables.
    finished_players (List[Player]) - Players who ran out of money or completed their rounds.
    casino_profit (int) - Total profit accumulated by the casino.
    total_hands_played (int) - Count of all hands played across every table.

Purpose:
    Acts as the central manager for the simulation, tracking tables, player states,
    and overall financial performance.
"""
from __future__ import annotations
from typing import List

from table import Table
from player import Player


class Casino:
    """
    Represents the overall casino that manages multiple blackjack tables,
    tracks total profit, and stores player statistics.
    """

    def __init__(self, casino_name: str) -> None:
        """
        Initialize a casino instance.

        Args:
            casino_name (str): The name of the casino.
        """
        self.casino_name: str = casino_name        # Name of the casino
        self.tables: List[Table] = []              # All active tables
        self.finished_players: List[Player] = []   # Players done playing
        self.casino_profit: int = 0                # Net casino profit across all tables
        self.total_hands_played: int = 0           # Global counter of all hands played
