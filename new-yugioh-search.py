import requests
import json
from datetime import datetime
import concurrent.futures

def fetch_group_ids():
    group_url = "https://tcgcsv.com/2/groups"
    response = requests.get(group_url).json()  # Fetch group data
    group_ids = [group['groupId'] for group in response['results']]  # Extract groupIds from the results
    return group_ids

# Function to fetch data for a single group
def fetch_group_data(group_id):
    product_url = f"https://tcgcsv.com/2/{group_id}/products"
    prices_url = f"https://tcgcsv.com/2/{group_id}/prices"

    try:
        products = requests.get(product_url).json()
        prices = requests.get(prices_url).json()
        return products['results'], prices['results']
    except Exception as e:
        print(f"Error fetching data for group {group_id}: {e}")
        return [], []  # Return empty lists if there's an error

def fetch_data():
    group_ids = fetch_group_ids()  # Get the list of group IDs

    all_products = []
    all_prices = []

    # Use ThreadPoolExecutor to fetch data concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a list of futures, one for each group_id
        futures = [executor.submit(fetch_group_data, group_id) for group_id in group_ids]

        # As each future completes, get its result
        for future in concurrent.futures.as_completed(futures):
            products, prices = future.result()
            all_products.extend(products)
            all_prices.extend(prices)

    return {'results': all_products}, {'results': all_prices}

def search_product(products, card_number):
    # Step 1: First try to match exact input rarity (mapped)
    for product in products['results']:
          # Loop through 'results' in the products dict
        extended_data = product.get("extendedData", [])

        product_card_number = None

        # Extract card number and rarity from extendedData
        for data in extended_data:
            if data.get("name") == "Number":
                product_card_number = data.get("value")

        if product_card_number:
            if product_card_number == card_number:
                # print(f"Found card number: {product_card_number}")
                return product

    print(f"No match found for card {card_number}")
    return None

# Step 6: Search for market price using productId
def search_price(prices, product_id):
    for price in prices['results']:
        if price["productId"] == product_id:
            return price.get("marketPrice", 0)
    return 0

# Read card list from txt file
def read_card_list(file_path):
    with open(file_path, "r") as file:
        cards = [line.strip().split() for line in file.readlines()]
    return cards

# Step 8 & 9: Export product information to txt file
def export_to_txt(outputFile, card_details, total_price, not_found_cards):
    today = datetime.now().strftime("%Y-%m-%d")
    found_cards = f"{outputFile}_found.txt"
    not_found_filename = f"{outputFile}_not_found.txt"

    # Sort card_details by market price in descending order
    sorted_card_details = sorted(card_details, key=lambda x: x['marketPrice'], reverse=True)

    # Write the found cards to card_details_output.txt
    with open(found_cards, "w") as file:
        file.write(f"Date: {today}\n\n")  # Write date and add an empty line
        file.write(f"Total price worth: ${total_price:.2f}\n\n")  # Write total price and add another empty line
        for product_info in sorted_card_details:
            file.write(f"{product_info['cleanName']}, {product_info['extendedData'][1]['value']}, {product_info['extendedData'][0]['value']}, ${product_info['marketPrice']:.2f}\n")

    # Write the not found cards to cards_not_found.txt
    with open(not_found_filename, "w") as not_found_file:
        not_found_file.write(f"Date: {today}\n")
        not_found_file.write("Cards not found:\n")
        for card in not_found_cards:
            not_found_file.write(f"Card Number: {card}\n")
    
    print(f"Data exported to {found_cards} and {not_found_filename}")

# Main program logic
def main(inputFile, outputFile):
    # Fetch products and prices
    products, prices = fetch_data()

    # Read card list from file
    cards = read_card_list(inputFile)

    card_details = []
    not_found_cards = []  # List to store not found cards
    total_price = 0

    for card in cards:
        card_number = card[0]

        # Step 4: Find the product
        product_info = search_product(products, card_number)

        if product_info:
            # Step 6: Find market price by productId
            market_price = search_price(prices, product_info["productId"])
            product_info['marketPrice'] = market_price
            card_details.append(product_info)
            
            # Step 10: Calculate the total market price
            total_price += market_price
        else:
            print(f"Card {card_number} not found!")
            not_found_cards.append((card_number))  # Add to not_found_cards list

    # Step 8 & 9: Export to txt file
    export_to_txt(outputFile, card_details, total_price, not_found_cards)

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    inputName = "yugioh-binder"
    inputFile = f"input/{inputName}.txt"
    outputFile = f"{inputName}_{today}"
    main(inputFile, outputFile)
