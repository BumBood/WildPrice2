from time import sleep

import requests

from db.products_db import Database
from parser.model import DBItem, Item

db = Database("db/products.db")


def get_info(art: int):
    response = requests.get(
        f'https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=29&nm={art}',
    )

    print(art, response.text)

    item_info = Item.model_validate(response.json()["data"]["products"][0])
    item_info.image_link = get_image_url(get_url(art))
    item_info.discount = get_sale(item_info.priceU, item_info.salePriceU)

    return item_info


def get_latest_price(art: int) -> int:
    try:
        url = get_url(art) + "info/price-history.json"
        prices_json = requests.get(url).json()

        latest_price = list(map(lambda x: x["price"]["RUB"] // 100, prices_json))[-1]

        return latest_price
    except Exception as e:
        print(e.__class__.__name__, e)
        return None


def get_url(art: int) -> str:
    art_str = str(art)
    part = art // 1000
    vol = art // 100000
    if 0 <= vol <= 143:
        basket = '01'
    elif 144 <= vol <= 287:
        basket = '02'
    elif 288 <= vol <= 431:
        basket = '03'
    elif 432 <= vol <= 719:
        basket = '04'
    elif 720 <= vol <= 1007:
        basket = '05'
    elif 1008 <= vol <= 1061:
        basket = '06'
    elif 1062 <= vol <= 1115:
        basket = '07'
    elif 1116 <= vol <= 1169:
        basket = '08'
    elif 1170 <= vol <= 1313:
        basket = '09'
    elif 1314 <= vol <= 1601:
        basket = '10'
    elif 1602 <= vol <= 1655:
        basket = '11'
    elif 1656 <= vol <= 1919:
        basket = '12'
    else:
        basket = '13'
    host = f'//basket-{basket}.wbbasket.ru'
    url = (f'https:{host}/vol{str(vol)}/'
           f'part{part}/{art_str}/')

    return url


def get_sale(previous_price, new_price) -> float:
    return (previous_price - new_price) / previous_price


def get_image_url(url: str) -> str:
    image_url = url + "images/big/1.webp"
    return image_url


def category_parser(name, shard, query):
    print([name, shard, query], "начало работу")
    if "subject" in query:
        query = str(query).replace('subject', 'cat')
    try:
        page = 1
        while True:
            try:
                print("page:", page)
                global resp
                try:
                    resp = requests.get(
                        f"https://catalog.wb.ru/catalog/{shard}/catalog?TestGroup=pk3_alpha05&TestID=351&appType=1&{query}&curr=rub&dest=-2534115&page={page}&sort=popular&spp=26")
                except Exception as e:
                    while True:
                        print("Произошла ошибка при подключении, продолжаю попытки до возобновления подключения\n",
                              e.__class__.__name__, e)
                        sleep(1)
                        try:
                            resp = requests.get(
                                f"https://catalog.wb.ru/catalog/{shard}/catalog?TestGroup=pk3_alpha05&TestID=351&appType=1&{query}&curr=rub&dest=-2534115&page={page}&sort=popular&spp=26")
                            break
                        except:
                            continue
                print(resp.status_code)
                if resp.status_code == 200:
                    json = resp.json()

                    products = json["data"]["products"]
                    for product in products:
                        item_info = DBItem.model_validate(product)
                        latest_price = get_latest_price(item_info.id)

                        if latest_price:
                            sale = get_sale(latest_price, item_info.salePriceU)

                            if sale >= 0.15:

                                check = db.add(item_info.id, item_info.name, item_info.salePriceU, latest_price,
                                               get_image_url(get_url(item_info.id)), query, name)

                                print("new sale")

                                if check == 1:
                                    db.update_price(item_info.id, item_info.salePriceU)
                                    db.update_previous_price(item_info.id, latest_price)

                                return
                            elif db.get_price_from_id(item_info.id):
                                db.delete_product_by_id(item_info.id)



                    page += 1
                else:
                    break
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(e.__class__.__name__, e)
        print([name, shard, query], "закончило работу")
        return 1

    except Exception as e:
        print(e)
        category_parser(name, shard, query)
