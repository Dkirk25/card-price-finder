from card import Card
from rarity_mapping import RARITY_MAPPING

class CardSearch:
    """Handles searching for a card within the fetched product data."""
    def __init__(self, products):
        self.products = products

    def search_product(self, card: Card):
        mapped_rarity = RARITY_MAPPING.get(card.rarity)
        # Step 1: First try to match exact input rarity (mapped)
        for product in self.products['results']:
            extended_data = product.get("extendedData", [])
            product_card_number = None
            product_rarity = None

            # Extract card number and rarity from extendedData
            for data in extended_data:
                if data.get("name") == "Number":
                    product_card_number = data.get("value")
                elif data.get("name") == "Rarity":
                    product_rarity = data.get("value")
                #CardEvent not equal Event

            if product_card_number:
                if product_card_number == card.card_number:
                    if card.rarity == None:
                        print(f"Exact match found for card {card.card_number}")
                        card.details = product
                        return product
                    # add check for card event not equal event or if it equals Character
                    elif product_rarity == mapped_rarity:
                        print(f"Exact match found for card {card.card_number} with rarity {mapped_rarity}")
                        card.details = product
                        return product

        if card.rarity != None:
            # Step 2: Try fallback rarities
            rarities = ["AP","SR*", "R**", "R*", "SR", "R", "U", "C"]
            for fallback_rarity in rarities:
                full_rarity = RARITY_MAPPING.get(fallback_rarity)
                for product in self.products['results']:
                    extended_data = product.get("extendedData", [])
                    product_card_number = None
                    product_rarity = None

                    for data in extended_data:
                        if data.get("name") == "Number":
                            product_card_number = data.get("value")
                        elif data.get("name") == "Rarity":
                            product_rarity = data.get("value")

                    if product_card_number == card.card_number and product_rarity == full_rarity:
                        print(f"Fallback match found for card {card.card_number} with rarity {full_rarity}")
                        card.details = product
                        return product

        print(f"No match found for card {card.card_number} with rarity {mapped_rarity}.")
        return None
