"""
simulation.py — Controls the main runtime loop of the Blackjack Casino Simulator.

This module is responsible for orchestrating the continuous simulation of casino activity,
coordinating the flow between blackjack rounds, player management, and user interface updates.

Core responsibilities:
    • Execute blackjack rounds across all tables concurrently.
    • Manage simulated time progression and configurable round delays.
    • Render real-time output views based on the selected mode:
        - Casino View: overall table summaries.
        - Table View: round-by-round details for one table.
        - Player View: live stats and hands for a tracked player.
    • Automatically refill and recycle broke or finished players back into play.
    • Persist all player and casino states to JSON for continuity across sessions.

In essence, this file functions as the simulation engine that connects
the casino, tables, players, blackjack logic, and UI display layers
into a single continuous system.
"""
from __future__ import annotations
from typing import List, Dict, Any

from time import sleep
import random

from blackjack import play_round
from table import Table
from player_factory import collect_all_players, save_player_pool_to_json
from casino import Casino
from run_config import RunConfig
from player import Player

from ui import (
    display_casino_round_summary,
    display_table_view,
    display_player_view,
)


def run_simulation(casino: Casino, player_pool: List[Player], run_config: RunConfig,
                   minutes: int, delay: float) -> int:
    """
    Run the full casino simulation loop.

    This function manages all simulation flow:
        - Fills empty table seats with players.
        - Repeatedly runs blackjack rounds for all tables.
        - Displays views (casino / table / player) based on configuration.
        - Refills broke or finished players periodically.
        - Saves player state to JSON after every round.

    Args:
        casino (Casino): The main casino instance containing tables and stats.
        player_pool (List[Player]): Waiting players not currently seated.
        run_config (RunConfig): Configuration defining which view mode to use.
        minutes (int): Total simulated duration (converted to rounds internally).
        delay (float): Delay in seconds between each simulated round (affects speed).

    Returns:
        int: Total simulated time in seconds.
    """

    refill_count: int = 0  # counts how many refill events occurred
    # each round = 10 simulated seconds
    rounds_to_play: int = (minutes * 60) // 10
    sim_time: int = 0  # total simulated seconds elapsed

    # Initially fill all tables with waiting players
    for table in casino.tables:
        table.fill_empty_seats(player_pool)

    # Run the simulation for the calculated number of rounds
    for _ in range(int(rounds_to_play)):

        # holds event data from all tables this round
        round_events: List[Dict] = []

        # Play a round on every active table
        for table in casino.tables:
            event = play_round(casino, table, player_pool)
            round_events.append(event)

        # Advance the simulated clock by 10 seconds per round
        sim_time += 10

        # Display results based on the selected view mode
        if run_config.view_mode == "casino":
            display_casino_round_summary(
                casino, run_config, round_events, sim_time, player_pool)

        elif run_config.view_mode == "table":
            for event in round_events:
                if event["table_id"] == run_config.tracked_table:
                    display_table_view(run_config, casino, event, sim_time)

        elif run_config.view_mode == "player":
            # Filter events related to the tracked player only
            filtered: List[Dict[str, Any]] = []
            for event in round_events:
                for result in event["results"]:
                    if result["player_name"].lower() == run_config.tracked_player.lower():
                        filtered.append(event)
                        break
            if filtered:
                display_player_view(run_config, casino,
                                    filtered, sim_time, player_pool)

        # Wait before the next simulated round (speed control)
        sleep(delay)

        # Every 1800 simulated seconds (30 min), revive finished players
        if sim_time % 1800 == 0:
            refill_count = 0
            # Refill finished players and move them back to player_pool
            revived_players: List[Player] = []

            # Give broke players money and rounds again
            for player in casino.finished_players:
                player.money_left += random.randint(500, 1000)
                player.rounds_left += random.randint(3, 10)
                revived_players.append(player)

            # Move revived players back to waiting pool
            for player in revived_players:
                casino.finished_players.remove(player)
                player_pool.append(player)

            if len(revived_players) > 0:
                print(
                    f"💰 {len(revived_players)} players have returned to the floor!")

        # Save updated player state to disk(json) after each round
        all_players: List[Player] = collect_all_players(casino, player_pool)
        save_player_pool_to_json(all_players, "data/players.json")

        # Ensure tables are refilled if seats open up
        for table in casino.tables:
            table.fill_empty_seats(player_pool)

    # Final save after all rounds complete
    all_players = collect_all_players(casino, player_pool)
    save_player_pool_to_json(all_players, "data/players.json")
    print("✅ Player pool saved.")

    return sim_time
