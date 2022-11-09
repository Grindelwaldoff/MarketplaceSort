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


class OZON():
    """
    Класс OZON.

    Обращается к API OZON и создает заказы
    на складе, также через API.
    """

    def __init__(self, current_date):
        self.current_date = current_date

    def get_list_request_ozon(self) -> dict:
        """Обращение к  API OZON."""
        since = (dt.utcnow() - timedelta(days=7)).isoformat() + 'Z'
        params = {
            "dir": "ASC",
            "filter":
            {
                "since": str(since),
                "status": "awaiting_packaging",
                "to": self.current_date
            },
            "limit": 100,
            "offset": 0
        }

        response = requests.post(
            url=BASE_URL_OZON,
            headers=HEADERS,
            json=params
        )
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError('Запрос к API не увенчался успехом.')

        self.get_orders_for_delivery(response=json.loads(response._content))

    def get_orders_for_delivery(self, response: dict) -> list:
        """Выборка заказов из результата  API. Также их валидация."""
        if not response.get('result'):
            raise Exception(
                    'OZON не ответил, результат не возвращается.'
                    'Запрос к API удачен.'
            )

        if response.get('result')['postings'] == []:
            raise KeyError('OZON не вернул товары. Заказов пока нет.')

        self.data_ordning_ozon(data=response.get('result')['postings'])

    def data_ordning_ozon(self, data: list) -> list:
        """Отфильтровывает ответ API, делая его более читабельными."""
        result = []
        for posting in self.data:
            product = {
                'name': posting['products']['name'],
                'article': posting['products']['offer_id'],
                'status': posting['status'],
                'posting_number': 'K-' + posting['posting_number'],
                'quantity': posting['products']['quantity'],
                'price': 100,
                'delivery_date': posting.get(
                    'delivering_date'
                    )[:10].replace('-', '.'),
            }
            result.append(product)

        self.send_request_to_storage(data=result)

    def send_request_to_storage(self, data: list) -> None:
        """Отправляет запрос к API Склада, создает заявку на доставку."""
        for product in self.data:
            params = {
                "partner_id": DELIVERY_PARTNER_ID,
                "key": DELIVERY_KEY,
                "order_number": product['posting_number'],
                "usluga": "ДОСТАВКА",
                "marketplace_id": OZON_MATVEEVSKAYA_MARKETPLACE,
                "sposob_dostavki": "Маркетплейс",
                "tip_otpr": "FBS с комплектацией",
                "cont_name": "Айбатыр",
                "cont_tel": "+7 (888) 888-88-40",
                "cont_mail": "test@yandex.ru",
                "region_iz": "Москва",
                "ocen_sum": 100,
                "picking": "Y",
                "free_date": "1",
                "date_dost": product['delivery_date'],
                "products": [
                    {
                        "name": product['name'],
                        "qty": product['quantity'],
                        "ed": "шт",
                        "code": product['article'],
                        "oc": 100,
                        "bare": "1000002055724",
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
    """Основная функция."""
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
        ozon_orders = OZON(current_date=current_date).get_list_request_ozon()
        get_result = OZON(response=ozon_orders).get_orders_for_delivery()
        sorted_products = OZON(data=get_result).data_ordning_ozon()
        OZON(data=sorted_products).send_request_to_storage()
        logging.info('Все окей, заказы создались.')
    except Exception as error:
        logging.error(error)


if __name__ == '__main__':
    main()
