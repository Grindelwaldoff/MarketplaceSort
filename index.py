import os
import logging
from datetime import datetime as dt, timedelta
from http import HTTPStatus
import base64
import time
import traceback

import requests

from constants.const_data import (
    DELIVERY_PARTNER_ID, DELIVERY_KEY,
    OZON_TOKEN, OZON_ID,
    OZON_MATVEEVSKAYA_MARKETPLACE,
    YANDEX_CAMP_ID, YANDEX_TOKEN,
    YANDEX_CLIENT_ID, YANDEX_MARKETPLACE
)
from constants.const_urls import (
    BASE_YANDEX_URL, BASE_URL_DELIVERY,
    BARCODE_DELIVERY_URL, BASE_URL_OZON
)


BASE_DIR = os.path.dirname(__file__)


class MakeOrdersForGuru():
    """Основной класс создания заказов для GURU."""

    def __init__(
        self,
        delivery_form,
        barcode_form,
    ) -> None:
        """Инициирующая функция."""
        self.delivery_form = delivery_form
        self.barcode_from = barcode_form

    def delivery_request_validation(order_list: list) -> dict:
        """Функция формирует заказ для склада."""
        result = []
        super().send_request_to_shipment(result)

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


def clean_pdf() -> None:
    """Очищает все штрих кода по завершению."""
    dirs = ['./yandex/pdf', './ozon/pdf', './sber/pdf']
    for dir in dirs:
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
    while True:
        try:
            clean_pdf()
        except Exception as error:
            logging.error(error)


if __name__ == '__main__':
    main()
