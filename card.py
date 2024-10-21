class Card:
    """Represents an individual card with its details and price."""
    def __init__(self, card_number, rarity, quanity, sub_type=None):
        self.card_number = card_number
        self.rarity = rarity
        self.sub_type = sub_type
        self.market_price = 0
        self.quantity = quanity
        self.details = None  # Will store the card details when found
