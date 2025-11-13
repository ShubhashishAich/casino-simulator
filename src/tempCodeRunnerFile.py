card_list = [
        ("A", 11), ("2", 2), ("3", 3), ("4", 4), ("5", 5), ("6", 6),
        ("7", 7), ("8", 8), ("9", 9), ("10", 10), ("J", 10), ("Q", 10), ("K", 10)
    ]
    suits = ["Heart", "Spade", "Club", "Diamond"]

    deck = []
    for suit in suits:
        for card, value in card_list:
            deck.append((card, suit, value))