"""
player.py - Defines the Player dataclass representing an individual casino participant.

Attributes:
    first_name (str) - Players first name.
    last_name (str) - Players last name.
    email (str) - Unique email for identification.
    player_id (int) - Unique player identifier.
    player_type (str) - Personality type: "casual", "regular", "aggressive", "high_roller".
    money_left (int) - Current balance of the player.
    rounds_left (int) - Remaining rounds before leaving the table.
    history (List[Tuple[str, int]]) - Records last 5 round outcomes as (result, bet).

Purpose:
    Provides a simple structured model for all players used across the casino simulation.
"""
from __future__ import annotations
from typing import List, Tuple

from dataclasses import dataclass, field


@dataclass
class Player:
    """
    Represents an individual blackjack player with identity,
    bankroll, and session configuration.
    """

    first_name: str
    last_name: str
    email: str
    player_id: int
    player_type: str  # "casual" ,"regular" , "aggressive" , "high_roller"
    money_left: int
    rounds_left: int

    # stores recent outcomes (win/loss/push, bet amount)
    history: List[Tuple[str, int]] = field(default_factory=list)
