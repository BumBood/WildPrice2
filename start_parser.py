from random import shuffle
from threading import Thread

from parser.wildberries_parser import category_parser
from parser.config import clothing_list

def start_cat_list_parser(cat_list: list):
    while True:
        shuffle(cat_list)
        for cat in cat_list:
            category_parser(*cat)

if __name__ == '__main__':
    clothing_thread = Thread(target=start_cat_list_parser, args=(clothing_list,), daemon=True)
    clothing_thread.start()
    clothing_thread.join()