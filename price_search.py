from card import Card

class PriceSearch:
    """Handles searching for the market price of a card."""
    def __init__(self, prices):
        self.prices = prices

    def search_price(self, card: Card):
        for price in self.prices['results']:
            if card.rarity == None:
                if price["productId"] == card.details["productId"]:
                    return price.get("marketPrice", 0)
            if price["productId"] == card.details["productId"] and card.rarity != "AP":
                return price.get("marketPrice", 0)
            elif price["productId"] == card.details["productId"] and price['subTypeName'] == "Normal":
                return price.get("marketPrice", 0)
        return 0
