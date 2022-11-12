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
BASE_URL_SBER = 'https://partner.goodsteam.tech/api/market/v1/orderService/order/search'

past_date = dt.utcnow() - timedelta(days=7)
date_from = str(past_date.isoformat('T', 'seconds') + 'Z')
current_date = str(dt.utcnow().isoformat('T', 'seconds')+'Z')

DELIVERY_PARTNER_ID = os.getenv('DELIVERY_ID')
DELIVERY_KEY = os.getenv('DELIVERY_TOKEN')
SBER_ID = os.getenv('SBER_ID')
SBER_TOKEN = os.getenv('SBER_TOKEN')

SBER_HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0'
}

SBER_PARAMS = {
    "data": {
        "token": str(SBER_TOKEN),
        "dateFrom": date_from,
        "dateTo": current_date,
        "count": 10,
        "statuses": [
            "CONFIRMED"
        ]
    },
    "meta": {}
}


def request() -> dict:
    """Функция запроса к API."""
    print(SBER_PARAMS)
    print(current_date)
    response = requests.post(
        url=BASE_URL_SBER,
        headers=SBER_HEADERS,
        json=SBER_PARAMS
    )

    if response.status_code != HTTPStatus.OK:
        raise ConnectionError(
            'Запрос к API не увенчался успехом.'
        )

    if not response.json():
        raise requests.JSONDecodeError(
            'Не удается преобразовать ответ API в JSON.'
        )

    print(response.json())

    return response.json()


def main():
    """Основная функция."""
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join(BASE_DIR, 'sber.log'),
        filemode='w',
        format=(
            'line:%(lineno)s \n'
            'time:%(asctime)s \n'
            'status:%(levelname)s \n'
            'info:%(message)s \n')
    )

    try:
        request()
    except Exception as error:
        logging.exception(error)


if __name__ == '__main__':
    main()
