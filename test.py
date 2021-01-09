import main
import os
import unittest
import sys
from dotenv import load_dotenv
load_dotenv(override=True)


list_of_card_numbers = open('final-card-values.txt', 'r').read().splitlines()

class TestSum(unittest.TestCase):

    def test_sorted_list(self):
        sorted_card_list = sorted(list_of_card_numbers, key=lambda k: float(k['price']), reverse= True) 
        self.assertEqual(3, len(map_of_balls))

if __name__ == '__main__':
    unittest.main()