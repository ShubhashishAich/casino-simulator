"""
blackjack.py — Implements the core game logic for running a single round of Blackjack within the casino simulation.
    - Dealing cards to players and the dealer
    - Simulating player actions (hit or stand based on simple AI logic)
    - Resolving wins, losses, and pushes
    - Updating player balances, casino profit, and round statistics

It acts as the main game engine, called repeatedly by `simulation.py` to advance the
simulation across multiple tables and players.

Event Lifecycle:-
    Each call to `play_round()` returns an event dictionary that captures everything that
    happened in that round:

        {
            "table_id": int,                # Which table played the round
            "round_num": int,               # Sequential round number
            "initial_bets": {seat: bet},    # Each player's initial bet amount
            "results": [                    # Round outcomes per seat
                {"seat_index": i, "player_name": str, "money_delta": ±int}
            ],
            "seats_after": [                # Player states after the round
                {"seat": i, "player": name or None, "money": int, "rounds": int}
            ],
            "profit_delta": int,            # Casino profit gained/lost this round
            "hands": {seat: [(rank, suit, value), ...]},   # Player hands
            "dealer_hand": [(rank, suit, value), ...]      # Dealer’s cards
        }

Main Function:-
    `play_round(casino, table, player_pool)`
    
    Runs a single blackjack round for the given table and updates the shared state.

    Args:
        casino (Casino): The global casino object tracking profit and overall stats.
        table (Table): The table instance containing seats and active players.
        player_pool (List[Player]): Waiting players who can fill empty seats.

    Returns:
        Dict: Structured event data describing everything that occurred in this round.

Responsibilities:-
    Create a fresh shuffled deck for each round  
    Generate random bets per active player  
    Deal cards to each seated player and to the dealer  
    Simulate simple player decision-making (hit until total ≥ 18)  
    Automatically resolve each hand (win / loss / push)  
    Update money balances, player histories, and casino profit  
    Remove broke or finished players and refill empty seats  
    Return a complete “round event” dictionary for logging and UI display

"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any

import random

from deck import Deck
from table import Table
from casino import Casino
from player import Player


def play_round(casino: Casino, table: Table, player_pool: List[Player]) -> Dict[str, Any]:
    """
    Execute a single round of blackjack at one table.

    Handles dealing, betting, win/loss resolution, and updates player/casino stats.

    Args:
        casino (Casino): The Casino object tracking profit and global stats.
        table (Table): The current table where the round is played.
        player_pool (List[Player]): The list of waiting players not currently seated.

    Returns:
        Dict[str, Any]: A structured event dictionary containing round data, hands, and outcomes.
    """

    event: Dict[str, Any] = {
        "table_id": table.table_id,
        "round_num": table.current_round_number,
        "initial_bets": {},
        "results": [],
        "seats_after": [],
        "profit_delta": 0,
        "hands": {},
        "dealer_hand": []
    }

    starting_profit: int = casino.casino_profit

    deck = Deck()
    deck.shuffle_deck()

    # Generate bets for each seated player
    for seat in table.seats_list:
        if seat.player is None:
            continue
        bet = random.randint(10, 100)
        event["initial_bets"][seat.seat_index] = bet

    player_hands: Dict[int, List[Tuple[str, str, int]]] = {}
    dealer_hand: List[Tuple[str, str, int]] = []

    # Deal two cards to each active player
    for seat in table.seats_list:
        if seat.player is not None:
            player_hands[seat.seat_index] = [
                deck.draw_card(), deck.draw_card()]

    # Deal two cards to the dealer
    for _ in range(2):
        dealer_hand.append(deck.draw_card())

    # Player Actions — each player hits until total >= 18 or busts (>21)
    for seat_index, hand in player_hands.items():
        casino.total_hands_played += 1
        total = 0
        for card in hand:
            total += card[2]
        while total < 18:
            new_card = deck.draw_card()
            hand.append(new_card)
            total = 0
            for card in hand:
                total += card[2]
            if total > 21:
                break

    # Dealer plays — hits until reaching at least 18
    dealer_total = 0
    for card in dealer_hand:
        dealer_total += card[2]
    while dealer_total < 18:
        dealer_hand.append(deck.draw_card())
        dealer_total = 0
        for card in dealer_hand:
            dealer_total += card[2]

    # Store full player hands (rank, suit, value tuples)
    for seat_index, hand in player_hands.items():
        event["hands"][seat_index] = list(hand)

    # Store dealer hand (full tuples)
    event["dealer_hand"] = list(dealer_hand)

    # Compare outcomes and adjust balances
    for seat_index, hand in player_hands.items():
        seat = table.seats_list[seat_index]
        player = seat.player
        bet = event["initial_bets"][seat_index]

        player_total = 0
        for card in hand:
            player_total += card[2]

        # default outcome (push)
        outcome: Tuple[str, int] = ("push", 0)

        # Player busts → casino wins
        if player_total > 21:
            player.money_left -= bet
            casino.casino_profit += bet
            outcome = ("loss", bet)
            event["results"].append(
                {"seat_index": seat_index,
                    "player_name": player.first_name, "money_delta": +bet}
            )

            # record outcome on player before continue
            player.history.append(outcome)
            if len(player.history) > 5:
                player.history = player.history[-5:]
            continue

        # Dealer busts → player wins
        if dealer_total > 21:
            player.money_left += bet
            casino.casino_profit -= bet
            outcome = ("win", bet)
            event["results"].append(
                {"seat_index": seat_index,
                    "player_name": player.first_name, "money_delta": -bet}
            )

            # record outcome on player before continue
            player.history.append(outcome)
            if len(player.history) > 5:
                player.history = player.history[-5:]
            continue

        # Player wins by higher total
        if player_total > dealer_total:
            player.money_left += bet
            casino.casino_profit -= bet
            outcome = ("win", bet)
            event["results"].append(
                {"seat_index": seat_index,
                    "player_name": player.first_name, "money_delta": -bet}
            )

            # record outcome on player before continue
            player.history.append(outcome)
            if len(player.history) > 5:
                player.history = player.history[-5:]
            continue

        # Player loses by lower total
        if player_total < dealer_total:
            player.money_left -= bet
            casino.casino_profit += bet
            outcome = ("loss", bet)
            event["results"].append(
                {"seat_index": seat_index,
                    "player_name": player.first_name, "money_delta": +bet}
            )

            # record outcome on player before continue
            player.history.append(outcome)
            if len(player.history) > 5:
                player.history = player.history[-5:]
            continue

        # Tie → push (no balance change)
        event["results"].append(
            {"seat_index": seat_index, "player_name": player.first_name, "money_delta": 0}
        )

        # record outcome on player before continue
        player.history.append(outcome)
        if len(player.history) > 5:
            player.history = player.history[-5:]

    # END OF ROUND CLEAN-UP
    # Decrease rounds left for active players
    for seat in table.seats_list:
        if seat.player is not None:
            seat.player.rounds_left -= 1

    # Update table and casino state
    table.remove_finished_players(player_pool, casino)
    table.fill_empty_seats(player_pool)

    table.current_round_number += 1

    # Build round event log:
    # Record final seat state for this round
    for seat in table.seats_list:
        if seat.player:
            event["seats_after"].append(
                {
                    "seat": seat.seat_index,
                    "player": seat.player.first_name,
                    "money": seat.player.money_left,
                    "rounds": seat.player.rounds_left
                }
            )
        else:
            event["seats_after"].append(
                {"seat": seat.seat_index, "player": None})

    # Casino profit delta for this round
    event["profit_delta"] = casino.casino_profit - starting_profit

    return event
