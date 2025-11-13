"""
ui.py — Handles all terminal display logic for the Blackjack Casino Simulator.

Contains all display and visualization functions for the Blackjack Casino Simulation.

Functions:
    • display_casino_round_summary() - Prints a summary of casino stats across all tables.
    • display_table_view() - Renders a detailed ASCII view of a single table.
    • display_player_view() - Shows one player's live stats, win rate, and last hand in ASCII.
    • ascii_cards() - Generates card-shaped ASCII art from (rank, suit, value) tuples.

Purpose:
    Handles all terminal output formatting for the simulation, providing clear and readable
    views for casino-wide, table-level, and player-level perspectives.
"""


from __future__ import annotations
from typing import Dict, List, Tuple, Any

from casino import Casino
from player import Player
from run_config import RunConfig


# CASINO VIEW — Displays overall casino summary across all tables

def display_casino_round_summary(casino: Casino, run_config: RunConfig,
                                 round_events: List[Dict[str, Any]], sim_time: int,
                                 player_pool: List[Player] | None = None) -> None:
    """
    Print a formatted summary of the entire casino after each round.

    Args:
        casino(Casino): The main Casino object containing global stats.
        run_config(RunConfig): Contains display preferences.
        round_events(List[Dict[str, Any]]): List of events produced this round.
        sim_time(int): Current simulated time in seconds.
        player_pool(List[Player] | None): Waiting players not currently seated.
    """

    # Convert simulated time (seconds) → HH:MM:SS
    hours = sim_time // 3600
    minutes = (sim_time % 3600) // 60
    seconds = sim_time % 60
    timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Count active players (seated at tables)
    active_players = 0
    for table in casino.tables:
        for seat in table.seats_list:
            if seat.player is not None:
                active_players += 1

    # Count waiting players
    if player_pool is not None:
        waiting_players = len(player_pool)
    else:
        waiting_players = 0

    # Count finished players
    finished_players = len(casino.finished_players)

    # PRINT SUMMARY HEADER
    print("\n" + "=" * 60)
    print(f"⏱  SIMULATION TIME: {timestamp}")
    print(f"🏦 CASINO PROFIT: {casino.casino_profit:+,}")
    print(f"🃏 HANDS PLAYED: {casino.total_hands_played:,}")
    print(
        f"🎲 Active: {active_players} | ⏳ Waiting: {waiting_players} | 🚪 Finished: {finished_players}")
    print("-" * 60)

    # PER TABLE SUMMARY
    for event in round_events:
        table_id = event["table_id"]
        seats_after = event["seats_after"]
        seated_players = sum(1 for s in seats_after if s["player"] is not None)
        total_seats = len(seats_after)
        profit_delta = event["profit_delta"]

        # Show how many players are seated and the profit change at each table
        print(
            f"Table {table_id} | Players {seated_players}/{total_seats} | Profit Δ {profit_delta:+}")

    # Footer separator for visual clarity
    print("=" * 60)


# TABLE VIEW — Detailed single-table round breakdown

def display_table_view(run_config: RunConfig, casino: Casino,
                       table_event: Dict[str, Any], sim_time: int) -> None:
    """
    Print a clean, fixed-width ASCII table view for a specific blackjack table.

    Args:
        run_config(RunConfig): View configuration settings.
        casino(Casino): Main Casino instance.
        table_event(Dict[str, Any]): Round data for this specific table.
        sim_time(int): Simulated clock time in seconds.
    """

    table_id: int = table_event["table_id"]
    seats_after: List[Dict[str, Any]] = table_event["seats_after"]
    results: List[Dict[str, Any]] = table_event["results"]
    profit_delta: int = table_event["profit_delta"]

    # Format simulated time
    hours = sim_time // 3600
    minutes = (sim_time % 3600) // 60
    seconds = sim_time % 60
    timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # fixed internal width for consistent formatting
    WIDTH: int = 61

    # TABLE HEADER
    print("\n" + "┌" + "─" * WIDTH + "┐")  # top border

    round_num = table_event["round_num"]
    header = f"TABLE {table_id} — ROUND {round_num}   ⏱ {timestamp}   Δ {profit_delta:+} Profit"
    print("│" + header.center(WIDTH) + "│")  # main header
    print("├" + "─" * WIDTH + "┤")  # header separator line

    # Column labels for seats
    print("│ Seat │ Player        │ Money      │ Rounds │ Outcome        │")
    print("│──────┼───────────────┼────────────┼────────┼────────────────│")

    # SEAT DETAILS
    for seat_info in seats_after:
        seat: int = seat_info["seat"]

        if seat_info["player"] is None:
            # Display empty seat placeholder
            print(
                f"│ {seat:^3}  │ {'- empty -':<13} │ {'-':>10} │ {'-':>6} │ {'':<13}  │")
            continue

        name: str = seat_info["player"]
        money: int = seat_info["money"]
        rounds: int = seat_info["rounds"]

        # Find the corresponding result for this seat
        outcome_text: str = "Push"
        for r in results:
            if r["seat_index"] == seat:
                delta = r["money_delta"]
                if delta > 0:
                    # positive means casino earned
                    outcome_text = f"Lost {delta}"
                elif delta < 0:
                    # negative means player won
                    outcome_text = f"Won {abs(delta)}"
                else:
                    # tie
                    outcome_text = "Push"
                break

        # Display formatted player stats in a row
        print(
            f"│ {seat:^3}  │ {name:<13} │ {money:>10,} │ {rounds:>6} │ {outcome_text:<13}  │")

    # Bottom border of table
    print("└" + "─" * WIDTH + "┘")

    # ROUND RESULT BOX
    print("\n┌" + "─" * WIDTH + "┐")
    print("│" + "ROUND RESULTS".center(WIDTH) + "│")
    print("├" + "─" * WIDTH + "┤")

    # Initialize result lists and totals
    winners: List[str] = []
    losers: List[str] = []
    pushes: List[str] = []
    total_winnings = 0
    total_losses = 0
    total_bets = 0

    # Parse results for display
    for r in results:
        # Finding player name for this seat
        player_name: str | None = None
        for seat_info in seats_after:
            if seat_info["seat"] == r["seat_index"] and seat_info["player"] is not None:
                player_name = seat_info["player"]
                break

        if player_name:
            delta = r["money_delta"]
            if delta < 0:  # Player won
                winners.append(f"{player_name} (+{abs(delta)})")
                total_winnings += abs(delta)
                total_bets += abs(delta)
            elif delta > 0:  # Player lost
                losers.append(f"{player_name} (-{delta})")
                total_losses += delta
                total_bets += delta
            else:  # Push
                pushes.append(player_name)

    # PRINT RESULTS SECTION
    # Display results - each line must be exactly WIDTH characters between borders
    if winners:
        # display all winners
        winners_text = "Winners: " + ", ".join(winners)
        # Pad to WIDTH characters, accounting for "│ " at start and " │" at end
        print(f"│ {winners_text:<{WIDTH-2}} │")

    if losers:
        # display all loosers
        losers_text = "Losers:  " + ", ".join(losers)
        # Pad to WIDTH characters, accounting for "│ " at start and " │" at end
        print(f"│ {losers_text:<{WIDTH-2}} │")

    if pushes:
        # display ties
        pushes_text = "Push:    " + ", ".join(pushes)
        # Pad to WIDTH characters, accounting for "│ " at start and " │" at end
        print(f"│ {pushes_text:<{WIDTH-2}} │")

    # Divider before totals
    print("├" + "─" * WIDTH + "┤")

    # METRICS SUMMARY
    metrics_bets = f"Total Bets: {total_bets:,}"
    print(f"│ {metrics_bets:<{WIDTH-2}} │")

    metrics_winnings = f"Total Winnings: {total_winnings:,}"
    print(f"│ {metrics_winnings:<{WIDTH-2}} │")

    metrics_losses = f"Total Losses: {total_losses:,}"
    print(f"│ {metrics_losses:<{WIDTH-2}} │")

    # Divider before final summary line
    print("├" + "─" * WIDTH + "┤")

    # Final summary of counts
    summary = f"Total: {len(winners)} Won | {len(losers)} Lost | {len(pushes)} Push"
    print(f"│ {summary:<{WIDTH-2}} │")
    print("└" + "─" * WIDTH + "┘")

    # Close box and print footer
    print(f"\nTOTAL CASINO PROFIT: {casino.casino_profit:+,}")
    print("-" * (WIDTH + 2))  # bottom border


# PLAYER VIEW — Displays one player's perspective and last hand in ASCII

def display_player_view(run_config: RunConfig, casino: Casino,
                        event_list: List[Dict[str, Any]], sim_time: int,
                        player_pool: List[Player]) -> None:
    """
    Display detailed, live statistics for a specific tracked player.

    The view shows:
        - Player state(PLAYING / WAITING / RESTING / IDLE)
        - Money and rounds remaining
        - Win rate(based on last 5 outcomes)
        - Average bet value
        - Last hand ( in ASCII card art)
        - Dealer's hand
        - Players recent outcomes
        - Current total casino profit

    Args:
        run_config (RunConfig): Configuration object containing the tracked player name.
        casino (Casino): The active Casino object tracking all tables and profits.
        event_list (List[Dict[str, Any]]): List of event dictionaries from recent rounds.
        sim_time (int): Current simulated time in seconds.
        player_pool (List[Player]): Players waiting to be seated.
    """

    # Extract the tracked player's name and the most recent event
    player_name: str = run_config.tracked_player
    latest_event: Dict[str, Any] = event_list[-1]

    # Convert simulated seconds into HH:MM:SS format
    hours = sim_time // 3600
    minutes = (sim_time % 3600) // 60
    seconds = sim_time % 60
    timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Locate player’s seat in latest event
    target_seat_info: Dict[str, Any] | None = None
    for seat in latest_event["seats_after"]:
        if seat["player"] == player_name:
            target_seat_info = seat
            break

    # Find the actual Player object in all lists
    player_obj: Player | None = None
    # Seated player search
    for table in casino.tables:
        for seat in table.seats_list:
            if seat.player is not None:
                if seat.player.first_name == player_name:
                    player_obj = seat.player
                    break

    # waiting pool search
    if player_obj is None:
        for p in player_pool:
            if p.first_name == player_name:
                player_obj = p
                break

    # finished list search
    if player_obj is None:
        for p in casino.finished_players:
            if p.first_name == player_name:
                player_obj = p
                break

    # player not found anywhere
    if player_obj is None:
        print(f"\n⚠️ Player {player_name} no longer in simulation.")
        return

    # Determine state (PLAYING / WAITING / RESTING / IDLE)
    if target_seat_info is None:
        money: int = player_obj.money_left
        rounds: int = player_obj.rounds_left

        if player_obj in player_pool:
            state = "WAITING"
        elif player_obj in casino.finished_players:
            state = "RESTING"
        else:
            state = "IDLE"
    else:
        money: int = target_seat_info["money"]
        rounds: int = target_seat_info["rounds"]
        state: str = "PLAYING"

    # Analyze player performance history
    history: List[tuple[str, int]] = player_obj.history

    # Determine last result text
    if len(history) > 0:
        last_outcome, last_amt = history[-1]
        if last_outcome == "win":
            outcome_label = f"✅ WIN +{last_amt}"
        elif last_outcome == "loss":
            outcome_label = f"❌ LOSS -{last_amt}"
        else:
            outcome_label = "⚖️ PUSH"
    else:
        outcome_label = ""

    total_hands: int = len(history)
    wins: int = 0
    losses: int = 0
    pushes: int = 0

    for h in history:
        if h[0] == "win":
            wins += 1
        elif h[0] == "loss":
            losses += 1
        else:
            pushes += 1

    if total_hands > 0:
        win_rate: float = (wins / total_hands) * 100
    else:
        win_rate: float = 0

    bets: List[int] = []
    for h in history:
        if h[1] > 0:
            bets.append(abs(h[1]))

    if len(bets) > 0:
        avg_bet: float = sum(bets) / len(bets)
    else:
        avg_bet: float = 0

    # DISPLAY UI — Build the player's visual summary box
    BOX_WIDTH: int = 78  # fixed width for neat alignment and room for card art

    print("\n" + "┌" + "─" * BOX_WIDTH + "┐")  # top border of the box

    # header text
    header: str = f"PLAYER VIEW — {player_name} ({state}) — {outcome_label}   ⏱ {timestamp}"
    # print centered header inside borders
    print("│ " + header.ljust(BOX_WIDTH - 2) + "│")

    print("├" + "─" * BOX_WIDTH + "┤")  # horizontal divider after header

    # Player statistics section
    print(f"│ Money Left: {money}".ljust(
        BOX_WIDTH - 1) + "│")  # current balance
    print(f"│ Rounds Left: {rounds}".ljust(
        BOX_WIDTH - 1) + "│")  # rounds remaining
    print("│" + "─" * BOX_WIDTH + "│")  # visual separator line
    print(f"│ Win Rate (last {total_hands} hands): {win_rate:.1f}%".ljust(
        BOX_WIDTH - 1) + "│")  # performance %
    print(f"│ Average Bet: {avg_bet:.2f}".ljust(
        BOX_WIDTH - 1) + "│")  # mean bet size

    print("├" + "─" * BOX_WIDTH + "┤")  # divider before card display section

    # Player’s last hand
    # seat index → list of cards
    hands: Dict[int, List[Tuple[str, str, int]]] = latest_event["hands"]
    seat_index: int | None = None
    # find player's seat index
    for r in latest_event["results"]:
        if r["player_name"] == player_name:
            seat_index = r["seat_index"]
            break

    print("│ Last Hand:".ljust(BOX_WIDTH - 1) + " │")  # label for hand display

    if seat_index is not None:  # if player played this round
        hand_cards: List[Tuple[str, str, int]] = hands.get(
            seat_index, [])  # retrieve player’s cards
        if hand_cards:  # if cards exist
            art: List[str] = ascii_cards(hand_cards)  # convert to ASCII art
            for line in art:  # print each visual line of the hand
                print("│ " + line.ljust(BOX_WIDTH - 3) + " │")
        else:
            # safety fallback if no hand found
            print("│   (Hand data missing)".ljust(BOX_WIDTH - 1) + " │")
    else:
        print("│   (Player did not play this round)".ljust(
            BOX_WIDTH - 1) + " │")  # player skipped this round

    # Dealer’s hand (only if player was active)
    if seat_index is not None:
        print("│ Dealer Hand:".ljust(BOX_WIDTH - 1) + " │")  # dealer header
        dealer_cards: List[Tuple[str, str, int]] = latest_event.get(
            "dealer_hand", [])  # dealer’s cards list
        art = ascii_cards(dealer_cards)  # convert dealer hand to ASCII
        for line in art:  # print each visual line
            print("│ " + line.ljust(BOX_WIDTH - 3) + " │")

    print("├" + "─" * BOX_WIDTH + "┤")  # divider before outcomes section

    # Recent results summary
    print("│ Recent Outcomes:".ljust(BOX_WIDTH - 1) + " │")  # section label
    for outcome, amt in history:  # iterate through recent player outcomes
        if outcome == "win":
            line = f"✅ WIN  +{amt}"  # player won
        elif outcome == "loss":
            line = f"❌ LOSS -{amt}"  # player lost
        else:
            line = f"⚖️ PUSH"  # tie (push)
        # print each outcome line neatly
        print(f"│ {line}".ljust(BOX_WIDTH - 1) + " │")

    print("└" + "─" * BOX_WIDTH + "┘")  # bottom border of the box

    # print total casino profit outside the box
    print(f"🏦 Casino Profit: {casino.casino_profit:+,}")


def ascii_cards(cards: List[Tuple[str, str, int]]) -> List[str]:
    """
    Generate ASCII-art representations of playing cards for terminal display.

    Each card is represented as a 5-line block using Unicode suit symbols and
    box-drawing characters, rendered horizontally next to each other.

    Example input:
        [ ("A", "Spade", 11),("10", "Heart", 10) ]

    Output:
        A list of strings, where each string corresponds to one line of the
        ASCII-rendered cards ready for printing line by line.

    Args:
        cards (List[Tuple[str, str, int]]): List of card tuples in the form
            (rank, suit, value).

    Returns:
        List[str]: Lines of ASCII art forming the visual representation of cards.
    """

    suit_symbols = {
        "Heart": "♥",
        "Diamond": "♦",
        "Club": "♣",
        "Spade": "♠"
    }

    # Each card is 5 lines tall; prepare empty placeholders
    lines: List[str] = ["", "", "", "", ""]

    # Build ASCII representation for each card and append horizontally
    for rank, suit, value in cards:
        s = suit_symbols[suit]
        r = rank

        card = [
            "┌─────────┐",
            f"│{r:<2}       │",
            f"│    {s}    │",
            f"│       {r:>2}│",
            "└─────────┘"
        ]

        for i in range(5):
            lines[i] += card[i] + " "  # Single space between cards

    return lines
