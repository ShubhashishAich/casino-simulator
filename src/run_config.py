"""
run_config.py - Defines the RunConfig class, which stores simulation view preferences
for the Blackjack Casino Simulator.

This configuration determines which type of interface to display:
    • "casino" — overview of all tables.
    • "table"  — focused view of a single table.
    • "player" — detailed statistics for one tracked player.
"""
from __future__ import annotations
from typing import Literal, Optional


class RunConfig:
    """
    Stores runtime display configuration for the simulator.

    Attributes:
        view_mode (Literal["casino", "table", "player"]):
            The current visualization mode for the simulation.
        tracked_table (Optional[int]):
            The ID of the table to follow if in "table" mode.
        tracked_player (Optional[str]):
            The first name of the player to follow if in "player" mode.
    """

    def __init__(self, view_mode: Literal["casino", "table", "player"] = "casino",
                 tracked_table: Optional[int] = None,
                 tracked_player: Optional[str] = None) -> None:
        self.view_mode = view_mode
        self.tracked_table = tracked_table
        self.tracked_player = tracked_player
