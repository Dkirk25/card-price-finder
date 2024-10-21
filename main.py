from datetime import datetime
from card_manager import CardManager

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    inputName = "bleach-box-1"
    group_product_number = 81
    union_arena_title = "Bleach"
    inputFile = f"input/{inputName}.txt"
    output_file = f"results/{inputName}_{today}"
    
    manager = CardManager(
        product_number=group_product_number,
        input_file=inputFile,
        output_file=output_file,
        union_arena_title=union_arena_title
    )
    manager.process()


# Input txt file structure, Card number, rarity, card quantity

# union_arena_title needs to be either Bleach, Hunter, jjk, or Code if product number is 81