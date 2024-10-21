from card_fetcher import CardFetcher
from card_search import CardSearch
from price_search import PriceSearch
from exporter import Exporter

class CardManager:
    """Main class that manages the overall card operations."""
    def __init__(self,  input_file, output_file, product_number,union_arena_title):
        self.input_file = input_file
        self.output_file = output_file
        self.product_number = product_number
        self.union_arena_title = union_arena_title
        self.card_fetcher = CardFetcher(product_number, union_arena_title)

    def process(self):
        products, prices = self.card_fetcher.fetch_data()
        card_list = Exporter.read_card_list(self.input_file)
        Exporter.write_sorted_cards(self.input_file, card_list)
        card_search = CardSearch(products)
        price_search = PriceSearch(prices)

        card_details = []
        not_found_cards = []
        total_price = 0

        for card in card_list:
            product_info = card_search.search_product(card)
            if product_info:
                card.market_price = price_search.search_price(card)
                card_details.append(card)
                total_price += card.market_price * card.quantity
            else:
                not_found_cards.append(card)

        Exporter.export_to_txt(self.output_file, card_details, total_price, not_found_cards)
