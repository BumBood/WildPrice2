from random import shuffle
from threading import Thread

from parser.model import parsing_list
from parser.wildberries_parser import category_parser


def start_cat_list_parser(cat_list: list):
    while True:
        shuffle(cat_list)
        for cat in cat_list:
            category_parser(*cat)


if __name__ == '__main__':
    clothing_thread = Thread(target=start_cat_list_parser, args=(parsing_list,), daemon=True)
    clothing_thread.start()
    clothing_thread.join()
