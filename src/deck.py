"""
deck.py - Defines the Deck class used to create and manage a multi-deck shoe for Blackjack.

Features:
    Builds a deck from 1 to 20 standard 52-card sets (default: 20 decks = 1,040 cards)
    Supports shuffling multiple times for randomness
    Allows drawing cards one by one during gameplay

Class:
    Deck
        - shuffle_deck() → Shuffles the deck three times.
        - draw_card() → Removes and returns the top card (rank, suit, value).

Each card is stored as a tuple: (rank, suit, value)
Example: ("K", "Spade", 10)

Used by: blackjack.py for dealing cards to players and the dealer.
"""
from __future__ import annotations
from typing import List, Tuple

import random


class Deck:
    """
    Represents a large blackjack shoe composed of multiple standard decks.
    Handles deck creation, shuffling, and drawing of cards.
    """

    # Each card defined by its rank and blackjack value
    CARD_LIST: List[Tuple[str, int]] = [
        ("A", 11), ("2", 2), ("3", 3), ("4", 4), ("5", 5), ("6", 6),
        ("7", 7), ("8", 8), ("9", 9), ("10", 10), ("J", 10), ("Q", 10), ("K", 10)
    ]

    # The four suits used in blackjack
    SUITS: List[str] = ["Heart", "Spade", "Club", "Diamond"]

    def __init__(self, num_decks: int = 20) -> None:
        """
        Initialize a shoe containing multiple decks (default = 20).

        Args:
            num_decks (int): Number of standard 52-card decks combined into one shoe.
        """
        self.deck: List[Tuple[str, str, int]] = []

        # build 20 decks (1040 cards)
        for _ in range(num_decks):
            for suit in self.SUITS:
                for card, value in self.CARD_LIST:
                    self.deck.append((card, suit, value))

    def shuffle_deck(self) -> None:
        """
        Shuffle the deck multiple times to ensure randomness.
        """

        # shuffle three times for better randomness
        for _ in range(3):
            random.shuffle(self.deck)

    def draw_card(self) -> Tuple[str, str, int]:
        """
        Draw one card from the top of the deck.

        Returns:
            Tuple[str, str, int]: A tuple containing (rank, suit, value).
        """
        drawn_card: Tuple[str, str, int] = self.deck.pop()
        return drawn_card
