"""
player_factory.py - Handles creation, management, and persistence of Player objects for the casino simulation.

Functions:
    generate_player() - Creates one randomized Player using Faker (name, email, type, money, rounds).
    generate_player_pool() - Builds a list of multiple players.
    save_player_pool_to_json() - Saves players to a JSON file.
    load_player_pool_from_json() - Loads players from JSON and rebuilds Player objects safely.
    collect_all_players() - Gathers all players (active, waiting, finished) into a single list.

Player types:
    "casual", "regular", "aggressive", "high_roller"
    Each type has its own money and round range to simulate realistic casino behavior.

This module keeps player data consistent, ensures all players have valid histories,
and supports saving and restoring game progress.
"""
from __future__ import annotations
from typing import List


from faker import Faker
import random
import json

from player import Player
from casino import Casino


fake = Faker()


def generate_player(player_id: int) -> Player:
    """
    Generate a single Player object with randomized type, balance, and round count.

    Args:
        player_id (int): Unique identifier assigned to the player.

    Returns:
        Player: A newly created Player object with randomized attributes.
    """

    player_type = random.choices(
        ["casual", "regular", "aggressive", "high_roller"],
        weights=[70, 20, 8, 2],
        k=1
    )[0]

    # Assign money and rounds based on player type
    if player_type == "casual":
        money = random.randint(1000, 2500)
        rounds = random.randint(5, 10)
    elif player_type == "regular":
        money = random.randint(2000, 4000)
        rounds = random.randint(10, 20)
    elif player_type == "aggressive":
        money = random.randint(3000, 8000)
        rounds = random.randint(8, 15)
    else:
        money = random.randint(8000, 20000)
        rounds = random.randint(15, 40)

    # Generate realistic random personal info
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()  # ensures no duplicates

    return Player(
        player_id=player_id,
        player_type=player_type,
        money_left=money,
        rounds_left=rounds,
        first_name=first_name,
        last_name=last_name,
        email=email
    )


def generate_player_pool(count: int) -> List[Player]:
    """
    Generate a pool of multiple random players.

    Args:
        count (int): Number of players to generate.

    Returns:
        List[Player]: List of generated Player objects.
    """

    pool: List[Player] = []
    # create players one by one
    for i in range(count):
        p = generate_player(i)
        pool.append(p)

    return pool


def save_player_pool_to_json(player_pool: List[Player], filename: str) -> None:
    """
    Save the current player pool to a JSON file.

    Args:
        player_pool (List[Player]): List of players to save.
        filename (str): Path to the output JSON file.
    """

    data = []
    for player in player_pool:
        data.append(player.__dict__)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def load_player_pool_from_json(filename: str) -> List[Player]:
    """
    Load a player pool from a JSON file and return Player objects.

    Args:
        filename (str): Path to the JSON file to load.

    Returns:
        List[Player]: List of Player objects loaded from the file.
    """

    with open(filename, "r") as f:
        data = json.load(f)

    player_pool: List[Player] = []

    # recreate Player objects from JSON data, adding an empty history list if missing
    for p in data:
        # Ensure missing "history" key doesn't crash
        if "history" not in p:
            p["history"] = []

        player = Player(**p)
        player_pool.append(player)

    return player_pool


def collect_all_players(casino: Casino, player_pool: List[Player]) -> List[Player]:
    """
    Collect all players currently in the casino, waiting pool, and finished list.

    Args:
        casino (Casino): The main casino object containing tables and finished players.
        player_pool (List[Player]): The list of unseated (waiting) players.

    Returns:
        List[Player]: Combined list of all players in the simulation.
    """

    all_players: List[Player] = []

    # gather all currently seated players from every table
    for table in casino.tables:
        for seat in table.seats_list:
            if seat.player is not None:
                all_players.append(seat.player)

    all_players.extend(player_pool)
    all_players.extend(casino.finished_players)

    return all_players
