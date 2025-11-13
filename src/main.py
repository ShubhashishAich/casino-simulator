"""
main.py — Orchestrates setup, configuration, and execution of the Blackjack Casino Simulation.
Entry point for the Blackjack Casino Simulation.

Handles:
    • Interactive setup of the casino environment.
    • Player pool generation or loading from saved data.
    • Simulation speed and view mode selection.
    • Initialization of the Casino and its tables.
    • Execution of the simulation via `run_simulation()`.

User chooses between three view modes:
    1) Casino View - Overview of all tables.
    2) Table View - Focused on a single table.
    3) Player View - Follows one specific player live.

Purpose:
    Provides the main CLI interface that configures and launches the entire simulation loop.

It interacts with supporting modules like:
- `player_factory.py` for generating/loading player data
- `simulation.py` for running the simulation loop
- `ui.py` for formatted output
"""
from __future__ import annotations
from typing import List, Optional


import sys
import shutil
import json
import time


from run_config import RunConfig
from casino import Casino
from player import Player
from player_factory import (
    generate_player_pool,
    save_player_pool_to_json,
    load_player_pool_from_json,
)
from simulation import run_simulation
from table import Table


# HELPER UI PRINT FUNCTIONS

def print_box(text: str, width: int = 60) -> None:
    """
    Print centered text inside a box of '=' characters.

    Args:
        text (str): The text to display.
        width (int, optional): Width of the box. Defaults to 60.
    """
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")


def print_line(width: int = 60) -> None:
    """Print a simple horizontal separator line."""
    print("-" * width)


def print_step(step_number: int, title: str) -> None:
    """
    Display a labeled step header for the current setup phase.

    Args:
        step_number (int): Step number in the setup flow.
        title (str): Step title to display.
    """
    print(f"\n{'=' * 60}")
    print(f"  STEP {step_number}: {title}")
    print("=" * 60 + "\n")


def print_option(number: str, text: str, description: str = "") -> None:
    """
    Print a numbered menu option with an optional description.

    Args:
        number (str): Option number or key.
        text (str): Main option text.
        description (str, optional): Additional explanation. Defaults to "".
    """
    print(f"  {number}) {text}")
    if description:
        print(f"      -> {description}")
    print()


# INPUT VALIDATION UTILITIES

def get_number_input(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """
    Prompt for a numeric value and validate its range.

    Args:
        prompt (str): Text shown to the user.
        min_val (int, optional): Minimum allowed value.
        max_val (int, optional): Maximum allowed value.

    Returns:
        int: The valid integer entered by the user.
    """
    while True:
        try:
            value = int(input(f"  {prompt}: "))
            if min_val is not None and value < min_val:
                print(
                    f"  [ERROR] Number must be at least {min_val}. Try again.")
                continue
            if max_val is not None and value > max_val:
                print(
                    f"  [ERROR] Number must be at most {max_val}. Try again.")
                continue
            return value
        except ValueError:
            print("  [ERROR] Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\n  Exiting program...")
            sys.exit(0)


def get_choice_input(prompt: str, valid_choices: List[str]) -> str:
    """
    Prompt the user to choose one of the valid string options.

    Args:
        prompt (str): The prompt to display.
        valid_choices (List[str]): Allowed string values.

    Returns:
        str: The chosen valid option.
    """
    while True:
        try:
            choice = input(f"  {prompt}: ").strip()
            if choice in valid_choices:
                return choice
            print(f"  [ERROR] Please enter one of: {', '.join(valid_choices)}")
        except KeyboardInterrupt:
            print("\n\n  Exiting program...")
            sys.exit(0)


def get_text_input(prompt: str) -> str:
    """
    Prompt the user for non-empty text input.

    Args:
        prompt (str): Message shown to the user.

    Returns:
        str: The entered text string.
    """
    while True:
        try:
            text = input(f"  {prompt}: ").strip()
            if text:
                return text
            print("  [ERROR] Please enter something.")
        except KeyboardInterrupt:
            print("\n\n  Exiting program...")
            sys.exit(0)

# MAIN PROGRAM EXECUTION FLOW


print_box("CASINO SIMULATOR", 60)
print("  Welcome! Let's set up your casino simulation.\n")


# 1) PLAYER POOL SETUP

print_step(1, "Player Pool Setup")

print_option("1", "Generate New Player Pool", "Create random players")
print_option("2", "Load Saved Player Pool", "Use existing players")

choice: str = get_choice_input("Enter your choice (1 or 2)", ["1", "2"])

if choice == "1":
    # Generate a new pool of random players
    count: int = get_number_input(
        "How many players to generate", min_val=1, max_val=1000)
    print(f"\n  Generating {count} players...")
    player_pool: List[Player] = generate_player_pool(count)
    save_player_pool_to_json(player_pool, "data/players.json")
    print(f"  [SUCCESS] Saved {count} players to data/players.json\n")

elif choice == "2":
    # Load player data from file
    print()
    print_option("1", "players.json", "Recently generated players")
    print_option("2", "premade_players.json", "Curated player pool")

    sub_choice: str = get_choice_input(
        "Which file to load? (1 or 2)", ["1", "2"])

    if sub_choice == "1":
        player_pool = load_player_pool_from_json("data/players.json")
        print(
            f"\n  [SUCCESS] Loaded {len(player_pool)} players from players.json\n")

    elif sub_choice == "2":
        shutil.copy("data/premade_players.json", "data/players.json")
        player_pool = load_player_pool_from_json("data/players.json")
        print(
            f"\n  [SUCCESS] Loaded {len(player_pool)} players from premade_players.json\n")


# 2) SIMULATION SPEED CONFIGURATION

print_step(2, "Simulation Speed")

print_option("1", "Slow (1.0 second per round)", "Watch every detail")
print_option("2", "Medium (0.5 seconds per round)", "Balanced viewing")
print_option("3", "Fast (0.15 seconds per round)", "Quick results")

speed_choice = get_choice_input("Select speed (1, 2, or 3)", ["1", "2", "3"])

if speed_choice == "1":
    delay = 1.0
    speed_name = "Slow"
elif speed_choice == "2":
    delay = 0.5
    speed_name = "Medium"
elif speed_choice == "3":
    delay = 0.15
    speed_name = "Fast"

print(f"\n  [SUCCESS] Speed set to {speed_name} ({delay} seconds per round)\n")


# 3) CASINO CONFIGURATION

print_step(3, "Casino Configuration")

casino_name: str = get_text_input("Enter your casino name")
print(f"\n  Creating casino: {casino_name}...\n")

casino = Casino(casino_name)

num_tables: int = get_number_input("How many tables", min_val=1, max_val=20)
print()

# Configure each table individually
for i in range(num_tables):
    print(f"  Configuring Table {i}:")
    seats = get_number_input(
        f"    Number of seats for Table {i}", min_val=1, max_val=10)
    casino.tables.append(Table(i, seats))
    print(f"    [SUCCESS] Table {i} created with {seats} seats\n")

# Display Casino Summary
print_line(60)
print(f"  CASINO SUMMARY")
print_line(60)
print(f"  Casino Name: {casino.casino_name}")
print(f"  Total Tables: {len(casino.tables)}")
print(f"  Total Players: {len(player_pool)}")
print_line(60)

for t in casino.tables:
    print(f"    Table {t.table_id}: {t.num_seats} seats")

print_line(60)
print()


# 4) VIEW MODE SELECTION

print_step(4, "View Mode Selection")

print_option("1", "Casino View", "See all tables at once")
print_option("2", "Table View", "Follow one specific table")
print_option("3", "Player View", "Follow one specific player")

view_choice: str = get_choice_input(
    "Select view mode (1, 2, or 3)", ["1", "2", "3"])

if view_choice == "1":
    run_config = RunConfig(view_mode="casino")
    print(f"\n  [SUCCESS] Casino View activated\n")

elif view_choice == "2":
    table_id: int = get_number_input(
        f"Enter table ID to follow (0 to {len(casino.tables)-1})",
        min_val=0,
        max_val=len(casino.tables)-1
    )
    run_config = RunConfig(view_mode="table", tracked_table=table_id)
    print(f"\n  [SUCCESS] Following Table {table_id}\n")

elif view_choice == "3":
    player_name: str = get_text_input("Enter player's first name to follow")
    run_config = RunConfig(view_mode="player", tracked_player=player_name)
    print(f"\n  [SUCCESS] Following player: {player_name}\n")


# 5) START SIMULATION

print_box("STARTING SIMULATION", 60)

print(f"  Casino: {casino.casino_name}")
print(f"  Speed: {speed_name}")
print(f"  Players: {len(player_pool)}")
print(f"  Tables: {len(casino.tables)}")
print()
print("  Press Ctrl+C to stop the simulation anytime")
print()
print_line(60)
print()

try:
    # Start real-world timer
    real_start: float = time.time()

    # Run the simulation
    simulated_seconds: int = run_simulation(
        casino, player_pool, run_config, minutes=32, delay=delay
    )

    # Stop real-world timer
    real_end: float = time.time()
    real_duration: float = real_end - real_start

    # Format real time nicely as MM:SS
    real_minutes: int = int(real_duration // 60)
    real_seconds: int = int(real_duration % 60)

    print()
    print_box("SIMULATION COMPLETE", 60)
    print(f"  Total simulated time: {simulated_seconds} seconds")
    print(f"  Real-world runtime: {real_minutes} min {real_seconds} sec")
    print(f"\n  Thank you for using Casino Simulator!\n")

except KeyboardInterrupt:
    print("\n")
    print_line(60)
    print("  Simulation stopped by user")
    print_line(60)
    print(f"\n  Thank you for using Casino Simulator!\n")
