import requests
import json
from datetime import datetime

# Rarity mapping based on input
rarity_mapping = {
    "R*": "Rare 1-Star",
    "SR": "Super Rare",
    "R": "Rare",
    "U": "Uncommon",
    "C": "Common",
    "AP": "Action Point"
}

# Step 1 & 2: Fetching data from the URLs
def fetch_data():
    product_url = "https://tcgcsv.com/81/23522/products"
    prices_url = "https://tcgcsv.com/81/23522/prices"

    products = requests.get(product_url).json()  # Save as a list of dictionaries
    prices = requests.get(prices_url).json()     # Save as a list of dictionaries

    return products, prices

def search_product(products, card_number, input_rarity):
    rarities = ["AP","R*", "SR", "R", "U", "C"]  # Search priority

    # Map input rarity to full name
    mapped_rarity = rarity_mapping.get(input_rarity)
    print(f"Searching for card: {card_number}, with rarity: {mapped_rarity}")

    # Step 1: First try to match exact input rarity (mapped)
    for product in products['results']:
          # Loop through 'results' in the products dict
        extended_data = product.get("extendedData", [])

        product_card_number = None
        product_rarity = None

        # Extract card number and rarity from extendedData
        for data in extended_data:
            if data.get("name") == "Number":
                product_card_number = data.get("value")
            elif data.get("name") == "Rarity":
                product_rarity = data.get("value")

        if product_card_number:
            if product_card_number == card_number:
                print(f"Found card number: {product_card_number}, rarity in data: {product_rarity}")

                if product_rarity == mapped_rarity:
                    print(f"Exact match found for card {card_number} with rarity {mapped_rarity}")
                    return product

    # Step 2: If no exact match, fallback to other rarities
    for rarity in rarities:
        full_rarity = rarity_mapping.get(rarity)
        for product in products['results']:  # Loop through 'results' in the products dict
            extended_data = product.get("extendedData", [])

            product_card_number = None
            product_rarity = None
            
            for data in extended_data:
                if data.get("name") == "Number":
                    product_card_number = data.get("value")
                elif data.get("name") == "Rarity":
                    product_rarity = data.get("value")

            if product_card_number:
                if product_card_number == card_number:
                    print(f"Checking fallback for card number: {product_card_number}, rarity in data: {product_rarity}")
                    if product_rarity == full_rarity:
                        print(f"Fallback match found for card {card_number} with rarity {full_rarity}")
                        return product

    print(f"No match found for card {card_number} with rarity {mapped_rarity} or fallbacks.")
    return None

# Step 6: Search for market price using productId
def search_price(prices, product_id, rarity, subtypeInput):
    for price in prices['results']:
        if price["productId"] == product_id and rarity != "AP":
            return price.get("marketPrice", 0)
        elif price["productId"] == product_id and price['subTypeName']== subtypeInput:
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
            not_found_file.write(f"Card Number: {card[0]}, Rarity: {card[1]}\n")
    
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
        rarity = card[1]
        # Subtype is only Foil or Normal
        subTypeInput = card[2] if len(card) > 2 else None

        if rarity == "AP" and not subTypeInput:
            raise ValueError(f"Error: Card {card_number} has an invalid rarity: {rarity} with no subtype input.")

        # Step 4: Find the product
        product_info = search_product(products, card_number, rarity)

        if product_info:
            # Step 6: Find market price by productId
            market_price = search_price(prices, product_info["productId"],rarity, subTypeInput)
            product_info['marketPrice'] = market_price
            card_details.append(product_info)
            
            # Step 10: Calculate the total market price
            total_price += market_price
        else:
            print(f"Card {card_number} with rarity {rarity} not found!")
            not_found_cards.append((card_number, rarity))  # Add to not_found_cards list

    # Step 8 & 9: Export to txt file
    export_to_txt(outputFile, card_details, total_price, not_found_cards)

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    inputFile = "union-arena-bleach.txt"
    outputFile = f"{inputFile}_{today}.txt"
    main(inputFile, outputFile)
