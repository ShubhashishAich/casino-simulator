"""
table.py - Defines the Table class, representing an individual blackjack table in the casino.

Attributes:
    table_id (int) - Unique identifier for the table.
    num_seats (int) - Total number of seats available.
    seats_list (List[Seat]) - List of Seat objects assigned to this table.
    current_round_number (int) - Tracks the round count for this table.

Methods:
    fill_empty_seats(player_pool) - Assigns waiting players to available seats.
    remove_finished_players(player_pool, casino) - Removes broke or done players and moves them to finished list.

Purpose:
    Manages seat assignments, player turnover, and round tracking for each blackjack table.
"""
from __future__ import annotations
from typing import List, TYPE_CHECKING

from seat import Seat
from player import Player
if TYPE_CHECKING:
    from casino import Casino


class Table:
    """
    Represents a blackjack table containing multiple seats and players.
    Each table can remove finished players and fill empty seats from the player pool.
    """

    def __init__(self, table_id: int, num_seats: int) -> None:
        """
        Initialize a new table with a specific number of seats.

        Args:
            table_id (int): Unique identifier for the table.
            num_seats (int): Number of seats available at the table.
        """

        self.table_id: int = table_id
        self.num_seats: int = num_seats
        self.seats_list: List[Seat] = []
        # create Seat objects for each seat index and add them to seats_list
        for i in range(num_seats):
            self.seats_list.append(Seat(i))
        self.current_round_number: int = 1  # starts from round 1

    def remove_finished_players(self, player_pool: List[Player], casino: Casino) -> None:
        """
        Remove players who have no money or rounds left, and move them to finished_players.

        Args:
            player_pool (List[Player]): The current waiting player pool.
            casino (Casino): The casino object that stores finished players.
        """

        # check each occupied seat and move players with low money or no rounds to finished_players
        for seat in self.seats_list:
            if seat.player is not None:
                if seat.player.money_left < 100 or seat.player.rounds_left <= 0:
                    player = seat.player
                    seat.player = None
                    casino.finished_players.append(player)

    def fill_empty_seats(self, player_pool: List[Player]) -> None:
        """
        Fill empty seats with players from the waiting pool.

        Args:
            player_pool (List[Player]): List of available players waiting to be seated.
        """

        # fill empty seats by assigning the next available player from the player_pool
        for seat in self.seats_list:
            if seat.player is None and len(player_pool) > 0:
                seat.player = player_pool.pop(0)
