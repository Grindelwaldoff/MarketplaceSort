import os
import logging
from datetime import datetime as dt, timedelta
from http import HTTPStatus
import base64
import time
import traceback
from functools import lru_cache

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(__file__)

DELIVERY_PARTNER_ID = os.getenv('DELIVERY_ID')
DELIVERY_KEY = os.getenv('DELIVERY_TOKEN')
TOKEN = os.getenv('OZON_TOKEN')
CLIENT_ID = os.getenv('OZON_CLIENT_ID')
HEADERS = {
    'Client-Id': CLIENT_ID,
    'Api-Key': TOKEN,
    'Content-Type': 'application/json'
}
OZON_MATVEEVSKAYA_MARKETPLACE = "49107"

BASE_URL_DELIVERY = ('https://api.dostavka.guru/client' +
                     '/in_up_market.php?json=yes')
BASE_URL_OZON = 'https://api-seller.ozon.ru/v3/posting/fbs/list'
BARCODE_DELIVERY_URL = 'https://api.dostavka.guru/methods/files/'


def get_list_request_ozon(current_date: str) -> dict:
    """Обращение к  API OZON."""
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

    return response.json()


def get_orders_for_delivery(response: dict) -> list:
    """Выборка заказов из результата  API. Также их валидация."""
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


def get_barcode(article: list) -> str:
    """Обращается к OZON и берет штрихкод у товара для его поиска на складе."""
    json = {
        "partner_id": DELIVERY_PARTNER_ID,
        "key": DELIVERY_KEY
    }

    try:
        response = requests.post(
            'https://api.dostavka.guru/methods/stocks/',
            json=json
        )

        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(
                'Запрос к API каталога склада не увенчался успехом.'
            )

        catalog = response.json()

        for item in catalog['msk-01']:  # не работает на тестовом аккаунте склада
            if item['article'] == article:
                return item['barcode']
    except Exception as error:
        raise Exception(error)


def download_pdf_barcode(posting_number: str):
    """Сохраняет штрихкода OZON в директорию pdf."""
    print(posting_number)
    json = {
        "posting_number": [
            posting_number
        ]
    }

    response = requests.post(
        'https://api-seller.ozon.ru/v2/posting/fbs/package-label',
        json=json,
        headers=HEADERS
    )

    if response.status_code == HTTPStatus.OK:
        with open(f'./ozon/pdf/{posting_number}.pdf', 'wb') as file:
            file.write(response.content)
        return True

    raise ConnectionError('Маркировка штрих-кода не скачалась.')


def json_barcode_from_ozon_to_delivery(posting_number: str) -> dict:
    """Подготавливает запрос к API склада для отправки штрихкода."""
    with open(f'./ozon/pdf/{posting_number}.pdf', 'rb') as file:
        barcode_json = {
            "partner_id": DELIVERY_PARTNER_ID,
            "key": DELIVERY_KEY,
            "format": "pdf",
            "type": 2,
            "copy": 1,
            "name": str(posting_number) + ".pdf",
            "order_number": "2l-" + posting_number,
            "file": base64.b64encode(file.read()).decode('UTF-8')
        }

    return barcode_json


def data_ordning_ozon(data: list) -> list:
    """Функция формирует заказ для склада."""
    result = []
    for posting in data:
        if download_pdf_barcode(posting['posting_number']):
            order = {
                "partner_id": DELIVERY_PARTNER_ID,
                "key": DELIVERY_KEY,
                "order_number": '2l-' + posting['posting_number'],
                "usluga": "ДОСТАВКА",
                "marketplace_id": OZON_MATVEEVSKAYA_MARKETPLACE,
                "sposob_dostavki": "Маркетплейс",
                "tip_otpr": "FBS с комплектацией",
                "cont_name": "Батыр",
                "cont_tel": "+7(964)775-52-25",
                "cont_mail": "bibalaev@gmail.com",
                "region_iz": "Москва",
                "ocen_sum": 100,
                "free_date": "1",
                "date_dost": posting["shipment_date"][:10].replace('-', '.'),
            }
            list_of_goods = []
            for product in posting['products']:
                goods = {
                        "name": product['name'],
                        "qty": product['quantity'],
                        "ed": "шт",
                        "code": product['offer_id'],
                        "oc": 100,
                        "bare": "00000000000",  # get_barcode(product['offer_id'])
                        "mono": 0,
                        "mark": 0,
                        "pack": 0
                }
                list_of_goods.append(goods)

            order.update({"products": list_of_goods})
            result.append(order)

    return result


def send_request_to_shipment(order: dict) -> str:
    """Отправляет запрос к API Склада, создает заявку на доставку."""
    response = requests.post(
        BASE_URL_DELIVERY,
        json=order,
    )
    answer = response.json()
    if 'errors' in answer:
        order.update({'date_dost': answer['str'][0][:-1:10]})
        requests.post(
            BASE_URL_DELIVERY,
            json=order,
        )

    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(
            'Запрос к API штрих кода склада не увенчался успехом.'
        )

    return (
        json_barcode_from_ozon_to_delivery(
            order['order_number'][3::]
        )
    )


def send_barcodes(json: dict) -> None:
    """Отправляет штрих-кода на склад."""
    response = requests.post(
        BARCODE_DELIVERY_URL,
        json=json,
    )
    print(response.json())

    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(
            'Запрос к API штрих-кода не увенчался успехом.'
        )


@lru_cache
def clean_pdf() -> None:
    """Очищает все штрих кода по завершению."""
    dir = './ozon/pdf'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


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
        barcodes_list = []
        clean_pdf()
        # Запрос к API OZON
        ozon_orders = get_list_request_ozon(current_date)
        # Получение списка товаров для длоставки
        get_products = get_orders_for_delivery(ozon_orders)
        # Формирование списка товаров для доставки, в ее формате
        make_order_list = data_ordning_ozon(get_products)
        # Отправление запроса к доставке, и загрузка штрих-кодов
        for order in make_order_list:
            barcodes_list.append(
                send_request_to_shipment(order)
            )
        time.sleep(10)
        for barcode in barcodes_list:
            send_barcodes(barcode)

        logging.info('Все окей, заказы создались.')
    except Exception as error:
        logging.error(error, traceback)


if __name__ == '__main__':
    main()
