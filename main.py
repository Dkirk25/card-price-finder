import requests
import string
import time
import os
import numpy as np
import multiprocessing

PARSER = 'html.parser'


def main():
    initial_list = open('cards.txt', 'r').read().splitlines()
    list_of_card_numbers = list(set(initial_list))

    processes = []
    number_of_processes = 5
    card_list_split_up = np.array_split(
        list_of_card_numbers, number_of_processes)
    q = multiprocessing.Queue()
    q2 = multiprocessing.Queue()
    for i in range(number_of_processes):
        processes.append(multiprocessing.Process(
            target=get_card_price, args=(card_list_split_up[i], q, q2)))

    for p in processes:
        p.start()

    liveprocs = list(processes)
    list_of_card_details = []
    list_of_unknown_cards = []
    while liveprocs:
        try:
            while 1:
                list_of_card_details.extend((q.get(False)))
                list_of_unknown_cards.extend((q2.get(False)))
        except Exception:
            pass
        time.sleep(0.5)    # Give tasks a chance to put more data in
        if not q.empty():
            continue
        liveprocs = [p for p in liveprocs if p.is_alive()]

    print("All processes finished execution!")

    # Sort by price
    sorted_card_list = sorted(
        list_of_card_details, key=lambda k: float(k['price']), reverse=True)

    print("Finish processing cards....")

    write_final_results(sorted_card_list, 'final-card-list.txt')

    write_missing_cards(list_of_unknown_cards, 'bad-cards.txt')


def get_card_price(list_of_cards, q, q2):
    temp_list = []
    missing_card_list = []
    for card_number in list_of_cards:

        payload = {"algorithm": "",
                   "from": 0,
                   "size": 24,
                   "filters": {
                       "term": {
                           "number": [
                                '{0}'.format(card_number)
                           ],
                           "productLineName": [
                               ""
                           ]
                       },
                       "range": {},
                       "match": {}
                   },
                   "listingSearch": {
                       "filters": {
                           "term": {},
                           "range": {
                               "quantity": {
                                   "gte": 1
                               }
                           },
                           "exclude": {
                               "channelExclusion": 0
                           }
                       },
                       "context": {
                           "cart": {}
                       }
                   },
                   "context": {
                       "cart": {},
                       "shippingCountry": "US"
                   },
                   "sort": {}}
        with requests.post(
                'https://mpapi.tcgplayer.com/v2/search/request?q=&isList=false', json=payload) as page:
            json_results = page.json()["results"][0]
            try:
                if len(json_results) > 0:
                    results = json_results["results"][0]

                    if len(results) > 0:
                        name = results["productUrlName"]
                        market_price = results["marketPrice"]
                        rarity = results["rarityName"]

                        card_details = {'name': name, 'price': market_price,
                                        'rarity': rarity, 'code': card_number}
                        temp_list.append(card_details)
            except Exception:
                print(card_number)
                missing_card_list.append(card_number)
    q.put(temp_list)
    q2.put(missing_card_list)


def write_final_results(list_of_card_results, file_name):
    prices = []
    f = open(file_name, 'w')
    for card_detail in list_of_card_results:
        f.write("{0}, {3}, {1}, {2}\n".format(
            card_detail['name'], card_detail['rarity'], card_detail['price'], card_detail['code']))
        price = card_detail["price"]
        prices.append(float(price))

    # print total price
    f.write("\nTotal price worth: {0}".format(sum(prices)))
    f.close()


def write_missing_cards(list_of_missing_cards, file_name):
    f = open(file_name, 'w')
    [f.write("{0}\n".format(number)) for number in list_of_missing_cards]
    f.close()


if __name__ == '__main__':
    main()
