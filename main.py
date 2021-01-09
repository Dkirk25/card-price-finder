import requests
from bs4 import BeautifulSoup
import string
import time
import  os
import _thread
import numpy as np
# import multiprocessing
from functools import partial
from itertools import product

PARSER = 'html.parser'

list_of_card_details = []
list_of_unknown_cards = []

def main():
    import multiprocessing

    global list_of_card_details
    global list_of_unknown_cards

    list_of_card_numbers = open('cards.txt', 'r').read().splitlines()

    processes = []
    number_of_processes = 5
    thread_lists = np.array_split(list_of_card_numbers, number_of_processes)
    q = multiprocessing.Queue()
    for i in range(number_of_processes):
        processes.append(multiprocessing.Process(target=get_card_price, args=(thread_lists[i],q)))

    for p in processes:
        p.start()

    liveprocs = list(processes)
    while liveprocs:
        try:
            while 1:
                list_of_card_details.extend((q.get(False)))
        except Exception as ex:
            pass
        time.sleep(0.5)    # Give tasks a chance to put more data in
        if not q.empty():
            continue
        liveprocs = [p for p in liveprocs if p.is_alive()]

    print("threads finished....")

    # both processes finished 
    print("Both processes finished execution!") 

    sorted_card_list = sorted(list_of_card_details, key=lambda k: float(k['price'][1:]), reverse= True) 

    print(len(sorted_card_list))
    print("Finish processing cards....")
    prices = []
    f = open('final-card-values.txt', 'w')
    for card_detail in sorted_card_list:
        f.write("{0}, {3}, {1}, {2}\n".format(card_detail['name'], card_detail['rarity'].split(" ", 1)[1], card_detail['price'], card_detail['code']))
        price = card_detail["price"]
        prices.append(float(price[1:]))

    # print total price
    f.write("\nTotal price worth: {0}".format(sum(prices)))
    f.close()

    f = open('bad-cards.txt', 'w')
    [f.write("{0}\n".format(number)) for number in list_of_unknown_cards]
    f.close()


def get_card_price(list_of_cards, q):
    global list_of_unknown_cards

    temp_list = []

    for card_number in list_of_cards:
        url = f"https://shop.tcgplayer.com/yugioh/product/show?advancedSearch=true&Number={card_number}"
        with requests.get(url, stream=True) as page:

            soup = BeautifulSoup(page.content, PARSER)
            try:
                name = soup.findAll(class_= "product__name")[0].text
                market_price = soup.findAll(class_= "product__market-price")[0].contents[3].text
                rarity = soup.findAll(class_= "product__extended-fields")[0].contents[3].text

                card_details = {'name':name, 'price': market_price, 'rarity': rarity, 'code': card_number}
                temp_list.append(card_details)
            except Exception as ex:
                print(ex)
                list_of_unknown_cards.append(card_number)
    q.put(temp_list)
    # q.put(None)
    print(len(temp_list))
    
if __name__ == '__main__':
    main()