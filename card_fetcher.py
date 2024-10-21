import requests
import concurrent.futures
from group_id_mapping import GroupIDMapping

class CardFetcher:
    BASE_URL = "https://tcgcsv.com/"

    """Fetches card product and price data from URLs."""
    def __init__(self, product_number, union_arena_title):
        self.product_number = product_number 
        self.union_arena_title = union_arena_title

    def fetch_group_ids(self):
        if self.product_number != 81:
            group_url = f"{self.BASE_URL}{self.product_number}/groups"
            response = requests.get(group_url).json()
            return [group['groupId'] for group in response['results']]
        else:
            # Do custom mapping for union arena cards.
            if self.union_arena_title == "Bleach":
                return [group['groupId'] for group in GroupIDMapping.BLEACH.value]
            elif self.union_arena_title == "Hunter":
                return [group['groupId'] for group in GroupIDMapping.HUNTER.value]
            elif self.union_arena_title == "jjk":
                return [group['groupId'] for group in GroupIDMapping.JJK.value]
            elif self.union_arena_title == "Code":
                return [group['groupId'] for group in GroupIDMapping.CODE.value]
            return []
    
    def fetch_group_data(self, group_id):
        product_url = f"{self.BASE_URL}{self.product_number}/{group_id}/products"
        prices_url = f"{self.BASE_URL}{self.product_number}/{group_id}/prices"
        try:
            products = requests.get(product_url).json()
            prices = requests.get(prices_url).json()
            return products['results'], prices['results']
        except Exception as e:
            print(f"Error fetching data for group {group_id}: {e}")
            return [], []
    
    def fetch_data(self):
        group_ids = self.fetch_group_ids()

        all_products = []
        all_prices = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetch_group_data, group_id) for group_id in group_ids]
            for future in concurrent.futures.as_completed(futures):
                products, prices = future.result()
                all_products.extend(products)
                all_prices.extend(prices)

        return {'results': all_products}, {'results': all_prices}
