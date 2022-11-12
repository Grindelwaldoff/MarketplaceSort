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

BASE_YANDEX_URL = ('https://api.partner.market.yandex.ru/v2'
                   f'/campaigns/{os.getenv("YANDEX_CAMPAIGN_ID")}/orders.json')

DELIVERY_PARTNER_ID = os.getenv('DELIVERY_ID')
DELIVERY_KEY = os.getenv('DELIVERY_TOKEN')
YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
YANDEX_CLIENT_ID = os.getenv('YANDEX_ID')

past_date = dt.utcnow() - timedelta(days=7)
date_from = str(past_date.strftime('%d-%m-%Y'))

YANDEX_PARAMS = {
    'fromDate': date_from,
    'status': 'PROCESSING',
    'substatus': 'READY_TO_SHIP'
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


def get_orders(request: dict) -> list:
    pass


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
        request(
            url=BASE_YANDEX_URL,
            headers=YANDEX_HEADERS,
            params=YANDEX_PARAMS
        )
    except Exception as error:
        logging.error(error, traceback)


if __name__ == '__main__':
    main()
