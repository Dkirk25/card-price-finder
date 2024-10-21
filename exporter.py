from datetime import datetime
from card import Card
import re
from collections import defaultdict

class Exporter:
    @staticmethod
    def write_sorted_cards(file_path, sorted_cards):
        """Write sorted cards back to the input file."""
        with open(file_path, "w") as file:
            for card in sorted_cards:
                file.write(f"{card.card_number} {card.rarity} {card.quantity}\n")

    """Reads and manages a list of cards from a file."""
    @staticmethod
    def alphanum_key(card):
        """Generate a key for alphanumeric sorting."""
        # Split card number into parts where numbers and text alternate, for proper sorting
        return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', card.card_number)]

    @staticmethod
    def read_card_list(file_path):
        card_dict = defaultdict(lambda: 0)  # Dictionary to accumulate quantities for duplicates

        with open(file_path, "r") as file:
            for line in file.readlines():
                parts = line.strip().split()

                if len(parts) == 3:  # Format: CardNumber Rarity Quantity
                    card_number, rarity, quantity = parts
                    quantity = int(quantity)
                elif len(parts) == 2:  # Missing quantity, default to 1
                    card_number, rarity = parts
                    quantity = 1
                else:
                    raise ValueError(f"Invalid card input format: {line.strip()}")

                # Create a unique key based on card_number and rarity
                card_key = (card_number, rarity)
                card_dict[card_key] += quantity  # Accumulate quantity for duplicates

        # Convert card_dict back into a list of Card objects
        sorted_cards = [Card(card_number, rarity, quantity) 
                        for (card_number, rarity), quantity in 
                        sorted(card_dict.items(), key=lambda item: Exporter.alphanum_key(Card(item[0][0], item[0][1], item[1])))]
        
        return sorted_cards

    """Handles exporting card data to a text file."""
    @staticmethod
    def export_to_txt(output_file, card_details, total_price, not_found_cards):
        today = datetime.now().strftime("%Y-%m-%d")
        found_cards_file = f"{output_file}_found.txt"
        not_found_file = f"{output_file}_not_found.txt"

        sorted_card_details = sorted(card_details, key=lambda x: x.market_price, reverse=True)

        with open(found_cards_file, "w") as file:
            file.write(f"Date: {today}\n\n")
            file.write(f"Total price worth: ${total_price:.2f}\n\n")
            for card in sorted_card_details:
                file.write(f"{card.details['cleanName']}, {card.details['extendedData'][1]['value']}, {card.quantity}, {card.details['extendedData'][0]['value']}, ${card.market_price:.2f}\n")
        if len(not_found_cards) > 0:
            with open(not_found_file, "w") as file:
                file.write(f"Date: {today}\n")
                file.write("Cards not found:\n\n")
                for card in not_found_cards:
                    if card.rarity == None:
                        file.write(f"Card Number: {card.card_number}\n")
                    else:
                        file.write(f"Card Number: {card.card_number}, Rarity: {card.rarity}\n")
            print(f"Data exported to {found_cards_file} and {not_found_file}")
