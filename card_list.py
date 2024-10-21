from card import Card
import re

class CardList:
    """Reads and manages a list of cards from a file."""
    @staticmethod
    def alphanum_key(card):
        """Generate a key for alphanumeric sorting."""
        # Split card number into parts where numbers and text alternate, for proper sorting
        return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', card.card_number)]

    @staticmethod
    def read_card_list(file_path):
        cards = []
        with open(file_path, "r") as file:
            for line in file.readlines():
                parts = line.strip().split()

                if len(parts) == 3:  # Format: CardNumber Rarity Quantity
                    card_number, rarity, quantity = parts
                    quantity = int(quantity)  # Ensure quantity is an integer
                elif len(parts) == 2:  # Missing quantity, default to 1
                    card_number, rarity = parts
                    quantity = 1  # Default quantity to 1 if not provided
                else:
                    raise ValueError(f"Invalid card input format: {line.strip()}")

                # Create a new Card object and append it to the list
                card = Card(card_number, rarity, quantity)
                cards.append(card)

            # Sort cards by card_number using the alphanumeric key function
            sorted_cards = sorted(cards, key=CardList.alphanum_key)
        return sorted_cards
