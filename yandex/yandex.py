import os
import logging
from datetime import datetime as dt, timedelta
from http import HTTPStatus
import base64
import time
import traceback

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(__file__)

YANDEX_CAMP_ID = os.getenv('YANDEX_CAMPAIGN_ID')

DELIVERY_PARTNER_ID = os.getenv('DELIVERY_ID')
DELIVERY_KEY = os.getenv('DELIVERY_TOKEN')
YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
YANDEX_CLIENT_ID = os.getenv('YANDEX_ID')
YANDEX_MARKETPLACE = os.getenv('YANDEX_MARKETPLACE')

past_date = dt.utcnow() - timedelta(days=7)
date_from = str(past_date.strftime('%d-%m-%Y'))

BASE_YANDEX_URL = ('https://api.partner.market.yandex.ru/v2'
                   f'/campaigns/{YANDEX_CAMP_ID}/orders.json')
BASE_URL_DELIVERY = ('https://api.dostavka.guru/client'
                     '/in_up_market.php?json=yes')
BARCODE_DELIVERY_URL = 'https://api.dostavka.guru/methods/files/'

YANDEX_PARAMS = {
    'fromDate': date_from,
    'status': 'PROCESSING',
    'substatus': 'READY_TO_SHIP',
    'page': 1
}

YANDEX_HEADERS = {
    'Authorization': (f'OAuth oauth_token={YANDEX_TOKEN},'
                      f'oauth_client_id={YANDEX_CLIENT_ID}'),
    'Content-Type': 'application/json;charset=utf-8'
}


def request(url: str, headers: dict, params: dict) -> dict:
    """Функция запроса."""
    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(
            'Запрос к API не увенчался успехом.'
        )

    if not response.json():
        raise requests.JSONDecodeError(
            'Не удается преобразовать ответ API в JSON.'
        )

    return response.json()


def get_orders(response: dict) -> list:
    """Забирает заказы из ответа YANDEX API."""
    if not response.get('orders'):
        raise Exception(
            'Yandex не вернул в ответе списко заказов.'
        )

    if not response.get('pager'):
        raise Exception(
            'Yandex не вернул pager в ответе.'
        )

    if response.get('orders') == []:
        logging.info('Заказов пока нет.')

    if not isinstance(response.get('orders'), list):
        raise TypeError('Yandex вернул список в другом формате.')

    return response['orders']


def get_barcode(article: list) -> str:
    """Обращается к YANDEX и берет штрихкод у товара для его поиска на складе."""
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


def get_barcode_yandex(order_id: str) -> None:
    url = ('https://api.partner.market.yandex.ru/v2'
           f'/campaigns/{YANDEX_CAMP_ID}/orders/{order_id}/delivery/labels')

    response = requests.get(url, headers=YANDEX_HEADERS)
    with open(f'./yandex/pdf/{order_id}.pdf', 'wb') as file:
        file.write(response._content)

    return json_barcode_to_delivery(order_id)


def json_barcode_to_delivery(order_id: str) -> dict:
    """Подготавливает запрос к API склада для отправки штрихкода."""
    with open(f'./yandex/pdf/{order_id}.pdf', 'rb') as file:
        barcode_json = {
            "partner_id": DELIVERY_PARTNER_ID,
            "key": DELIVERY_KEY,
            "format": "pdf",
            "type": 0,
            "copy": 1,
            "name": order_id + ".pdf",
            "order_number": "Y-" + order_id,
            "file": base64.b64encode(file.read()).decode('UTF-8')
        }

    return send_barcodes(barcode_json)


def send_barcodes(json: dict) -> None:
    """Отправляет штрих-кода на склад."""
    response = requests.post(
        BARCODE_DELIVERY_URL,
        json=json,
    )

    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(
            'Запрос к API штрих-кода не увенчался успехом.'
        )


def data_valid(data: int) -> str:
    result = data[6::] + '.' + data[3:5] + '.' + data[:2]
    return str(result)


def delivery_request_validation(order_list: list) -> dict:
    result = []
    for posting in order_list:
        order_form = {
            "partner_id": DELIVERY_PARTNER_ID,
            "key": DELIVERY_KEY,
            "order_number": 'Y-' + str(posting['id']),
            "usluga": "ДОСТАВКА",
            "marketplace_id": YANDEX_MARKETPLACE,
            "sposob_dostavki": "Маркетплейс",
            "tip_otpr": "FBS с комплектацией",
            "cont_name": "Батыр",
            "cont_tel": "+7(964)775-52-25",
            "cont_mail": "bibalaev@gmail.com",
            "region_iz": "Москва",
            "ocen_sum": 100,
            "free_date": "2",
            "date_dost": data_valid(
                posting['delivery']['shipments']
                [0]['shipmentDate'].replace('-', '.')),
        }
        print(order_form['date_dost'])
        list_of_goods = []
        for item in posting['items']:
            goods = {
                    "name": "Товар",
                    "qty": item['count'],
                    "ed": "шт",
                    "code": item['offerId'],
                    "oc": 100,
                    "bare": get_barcode(item['offerId']),  # get_barcode(item['offerId'])
                    "mono": 0,
                    "mark": 0,
                    "pack": 0
            }
            list_of_goods.append(goods)

        order_form.update({"products": list_of_goods})
        result.append(order_form)

    return result


def send_request_to_shipment(order: dict) -> str:
    """Отправляет запрос к API Склада, создает заявку на доставку."""
    response = requests.post(
        BASE_URL_DELIVERY,
        json=order,
    )
    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(
            'Запрос к API штрих кода склада не увенчался успехом.'
        )

    time.sleep(10)
    get_barcode_yandex(order['order_number'][2::])


def clean_pdf() -> None:
    """Очищает все штрих кода по завершению."""
    dir = './yandex/pdf'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


def main():
    """Основная функция."""
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join(BASE_DIR, 'yandex.log'),
        filemode='w',
        format=(
            'line:%(lineno)s \n'
            'time:%(asctime)s \n'
            'status:%(levelname)s \n'
            'info:%(message)s \n')
    )

    try:
        clean_pdf()
        response = request(
            url=BASE_YANDEX_URL,
            headers=YANDEX_HEADERS,
            params=YANDEX_PARAMS
        )
        order_pages = [get_orders(response)]

        if response['pager']['pagesCount'] != response['pager']['currentPage']:
            while (response['pager']['pagesCount']
                    == response['pager']['currentPage']):
                response = request(
                    url=BASE_YANDEX_URL,
                    headers=YANDEX_HEADERS,
                    params=YANDEX_PARAMS.update(
                        {'page': response['pager']['currentPage'] + 1}
                    )
                )
                check_response = get_orders(response)
                order_pages.append(check_response)

        for page in order_pages:
            delivery_order_list = delivery_request_validation(page)
            for order in delivery_order_list:
                send_request_to_shipment(order)

    except Exception as error:
        logging.error(error, traceback)


if __name__ == '__main__':
    main()
