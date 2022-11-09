import os
import json
import logging
from datetime import datetime as dt, timedelta
from http import HTTPStatus

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(__file__)

DELIVERY_PARTNER_ID = "9999"
DELIVERY_KEY = "cc03e747a6afbbcbf8be7668acfebee5"
OZON_MATVEEVSKAYA_MARKETPLACE = "49107"
TOKEN = os.getenv('TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
HEADERS = {
    'Client-Id': CLIENT_ID,
    'Api-Key': TOKEN,
    'Content-Type': 'application/json'
}

BASE_URL_DELIVERY = ('https://api.dostavka.guru/client' +
                     '/in_up_market.php?json=yes')
BASE_URL_OZON = 'https://api-seller.ozon.ru/v3/posting/fbs/list'


def get_list_request_ozon(current_date: str) -> dict:
    since = (dt.utcnow() - timedelta(days=7)).isoformat() + 'Z'
    params = {
        "dir": "ASC",
        "filter":
        {
            "since": str(since),
            "status": "awaiting_deliver",
            "to": current_date
        },
        "limit": 100,
        "offset": 0
    }

    response = requests.post(url=BASE_URL_OZON, headers=HEADERS, json=params)
    if response.status_code != HTTPStatus.OK:
        raise ConnectionError('Запрос к API не увенчался успехом.')

    return json.loads(response._content)


def get_orders_for_delivery(response: dict) -> list:
    if not response.get('result'):
        raise Exception(
                'OZON не ответил, результат не возвращается.'
                'Запрос к API удачен.'
        )

    if response.get('result')['postings'] == []:
        raise KeyError('OZON не вернул товары. Заказов пока нет.')

    if not isinstance(response.get('result')['postings'], list):
        raise TypeError('OZON вернул не список.')

    return response.get('result')['postings']


def data_ordning_ozon(data: list) -> list:
    result = []
    for product in data:
        product = {
            'name_of_product': product['products'][0]["name"],
            'article': product['products'][0]["offer_id"],
            'order_number': 'K-' + product["posting_number"],
            'quantity': product['products'][0]["quantity"],
            'delivery_date': product["shipment_date"][:10].replace('-', '.'),
        }
        result.append(product)

    return result


def send_request_to_shipment(data: list) -> None:
    for product in data:
        print(product['delivery_date'])
        params = {
            "partner_id": DELIVERY_PARTNER_ID,
            "key": DELIVERY_KEY,
            "order_number": product['order_number'] + '234dsf',
            "usluga": "ДОСТАВКА",
            "marketplace_id": OZON_MATVEEVSKAYA_MARKETPLACE,
            "sposob_dostavki": "Маркетплейс",
            "tip_otpr": "FBS с комплектацией",
            "cont_name": "Айбатыр",
            "cont_tel": "+7 (888) 888-88-40",
            "cont_mail": "test@yandex.ru",
            "region_iz": "Москва",
            "ocen_sum": 100,
            "free_date": "1",
            "date_dost": product['delivery_date'],
            "products": [
                {
                    "name": product['name_of_product'],
                    "qty": product['quantity'],
                    "ed": "шт",
                    "code": product['article'],
                    "oc": 100,
                    "bare": "000000",
                    "mono": 0,
                    "mark": 0,
                    "pack": 0
                }
            ]
        }

        requests.post(
            BASE_URL_DELIVERY,
            json=params,
        )


def main():
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join(BASE_DIR, 'main.log'),
        filemode='w',
        format=(
            'line:%(lineno)s \n'
            'time:%(asctime)s \n'
            'status:%(levelname)s \n'
            'info:%(message)s \n')
    )

    current_date = str(dt.utcnow().isoformat()+'Z')

    try:
        ozon_orders = get_list_request_ozon(current_date)
        get_products = get_orders_for_delivery(ozon_orders)
        sorted_products = data_ordning_ozon(get_products)
        send_request_to_shipment(sorted_products)
        logging.info('Все окей, заказы создались.')
    except Exception as error:
        logging.error(error)


if __name__ == '__main__':
    main()
