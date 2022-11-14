import os
import logging
from datetime import datetime as dt, timedelta
from http import HTTPStatus
import base64
import sys
import time
import traceback
from random import randint

import requests

from constants.data import (
    DELIVERY_PARTNER_ID, DELIVERY_KEY,
    OZON_TOKEN, OZON_ID,
    OZON_HEADERS, OZON_PARAMS,
    OZON_MATVEEVSKAYA_MARKETPLACE,
    YANDEX_CAMP_ID, YANDEX_TOKEN,
    YANDEX_CLIENT_ID, YANDEX_MARKETPLACE,
    YANDEX_HEADERS, YANDEX_PARAMS
)
from constants.urls import (
    BASE_YANDEX_URL, BASE_URL_DELIVERY,
    BARCODE_DELIVERY_URL, BASE_URL_OZON
)


BASE_DIR = os.path.dirname(__file__)


class MakeOrdersForGuru():
    """Основной класс создания заказов для GURU."""

    current_date = dt.utcnow().isoformat('T', 'seconds')
    past_date = dt.utcnow() - timedelta(days=7)
    date_from = str(past_date.strftime('%d-%m-%Y'))

    def market_place_request(self) -> dict:
        """Функция запроса."""
        raise KeyError('Marketplace undefined.')

    def get_orders(self, response: dict) -> list:
        """Забирает заказы из ответа API."""
        raise KeyError('Marketplace undefined.')

    def item_form_validation(
        self, amount: int, offer_id: str
    ) -> list:
        """Формирует список товаров."""
        item = {
            "name": "Товар",
            "qty": amount,
            "ed": "шт",
            "code": offer_id,
            "oc": 100,
            "bare": self.get_barcode_delivery_catalog(offer_id),  # self.get_barcode_delivery_catalog(offer_id)
            "mono": 0,
            "mark": 0,
            "pack": 0
        }
        return item

    def delivery_form_validation(
        self, order_number: str, date_dost: str, items_list: list
    ) -> dict:
        """Формирует запрос для GURU."""
        order_form = {
            "partner_id": DELIVERY_PARTNER_ID,
            "key": DELIVERY_KEY,
            "order_number": order_number,
            "usluga": "ДОСТАВКА",
            "marketplace_id": YANDEX_MARKETPLACE,
            "sposob_dostavki": "Маркетплейс",
            "tip_otpr": "FBS с комплектацией",
            "cont_name": "Батыр",
            "cont_tel": "+7(964)775-52-25",
            "cont_mail": "bibalaev@gmail.com",
            "region_iz": "Москва",
            "ocen_sum": 100,
            "free_date": "0",
            "date_dost": date_dost
        }
        order_form.update({"products": items_list})

        return order_form

    def get_barcode_marketplace(
        self, name: str,
        order_id: str, prefix: str
    ) -> None:
        """Функция скачивает штрих-кода из магазина."""
        raise KeyError('Marketplace undefined.')

    def get_barcode_delivery_catalog(self, article: str) -> str:
        """Берет штрих-код из каталога склада."""
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

    def write_down_barcode_file(
        self, name: str,
        order_id: str, prefix: str,
        response
    ) -> None:
        with open(f'./{name}/pdf/{order_id}.pdf', 'wb') as file:
            file.write(response._content)

        return self.json_barcode_to_delivery(name, order_id, prefix=prefix)

    def json_barcode_to_delivery(
        self, name, order_id: str, prefix: str
    ) -> dict:
        """Подготавливает запрос к API склада для отправки штрихкода."""
        with open(f'./{name}/pdf/{order_id}.pdf', 'rb') as file:
            barcode_json = {
                "partner_id": DELIVERY_PARTNER_ID,
                "key": DELIVERY_KEY,
                "format": "pdf",
                "type": 0,
                "copy": 1,
                "name": order_id + ".pdf",
                "order_number": prefix + order_id,
                "file": base64.b64encode(file.read()).decode('UTF-8')
            }

        return barcode_json

    def send_barcode(self, barcode_forms: dict) -> None:
        """Отправляет штрих-кода на склад."""
        for form in barcode_forms:
            response = requests.post(
                BARCODE_DELIVERY_URL,
                json=form,
            )

            return response

            # if response.status_code != HTTPStatus.OK:
            #     raise ConnectionError(
            #         'Запрос к API отвечающим за штрих-код'
            #         ' не увенчался успехом.'
            #     )

    def send_request_to_shipment(
        self, delivery_forms: list,
    ) -> None:
        """Отправляет запрос к API Склада, создает заявку на доставку."""
        for form in delivery_forms:
            response = requests.post(
                BASE_URL_DELIVERY,
                json=form,
            )
            # if response.status_code != HTTPStatus.OK:
            #     raise ConnectionError(
            #         'Запрос к API склада не увенчался успехом.'
            #     )

            print(response.json(), BARCODE_DELIVERY_URL)

            if 'errors' in response.json():
                logging.error(response.json()['str'])

    def make_order(self, delivery_forms: list, barcode_forms: list) -> None:
        """Основная функция класса - отправляет запросы к API."""
        self.send_request_to_shipment(delivery_forms=delivery_forms)
        time.sleep(0)
        self.send_barcode(barcode_forms=barcode_forms)


class Yandex(MakeOrdersForGuru):
    """Получение списка заказов с Яндекс."""

    def market_place_request(self) -> dict:
        """Функция запроса."""
        response = requests.get(
            BASE_YANDEX_URL,
            headers=YANDEX_HEADERS,
            params=YANDEX_PARAMS
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

    def get_orders(self, response: dict) -> MakeOrdersForGuru:
        """Забирает заказы из ответа Yandex API."""
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

    def get_barcode_marketplace(
        self, name: str, order_id: str, prefix: str
    ) -> None:
        """Функция скачивает штрих-кода из магазина."""
        url = (
            'https://api.partner.market.yandex.ru/v2'
            f'/campaigns/{YANDEX_CAMP_ID}/orders/{order_id}/delivery/labels'
        )

        response = requests.get(url, headers=YANDEX_HEADERS)
        return self.write_down_barcode_file(
            name=name, order_id=order_id,
            prefix=prefix, response=response
        )

    def data_valid(self, data: int) -> str:
        """Меняет формат даты, который вернул API."""
        result = data[6::] + '.' + data[3:5] + '.' + data[:2]
        return str(result)

    def order_data_compose(
        self,
        page_list: list
    ) -> MakeOrdersForGuru:
        """Вытягивает данные из ответа API для доставки."""
        delivery_forms = []
        barcodes_forms = []
        for order in page_list:
            items_list = []
            date_dost = self.data_valid(
                order['delivery']['shipments']
                [0]['shipmentDate'].replace('-', '.')
            )
            for item in order['items']:
                items_list.append(self.item_form_validation(
                    amount=item['count'],
                    offer_id=str(item['offerId'])
                ))

            delivery_forms += [
                super().delivery_form_validation(
                    order_number=('Y-' + str(order['id'])),
                    date_dost=date_dost,
                    items_list=items_list
                )
            ]
            barcodes_forms.append(
                self.get_barcode_marketplace(
                    name='yandex',
                    order_id=str(order['id']),
                    prefix='Y-'
                )
            )

        return self.make_order(delivery_forms, barcodes_forms)


class Ozon(MakeOrdersForGuru):
    """Класс для получения заказов с OZON."""

    def market_place_request(self) -> dict:
        """Обращение к  API OZON."""
        response = requests.post(
            url=BASE_URL_OZON,
            headers=OZON_HEADERS,
            json=OZON_PARAMS
        )
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError('Запрос к API не увенчался успехом.')

        return self.get_orders(response.json())

    def get_orders(self, response: dict) -> list:
        """Выборка заказов из результата  API. Также их валидация."""
        if not response.get('result'):
            raise Exception(
                'OZON не ответил, результат не возвращается.'
                'Запрос к API удачен.'
            )

        if response.get('result')['postings'] == []:
            logging.info('Заказов пока нет.')

        if not isinstance(response.get('result')['postings'], list):
            raise TypeError('OZON вернул список заказов в другом формате.')

        return self.order_data_compose(response.get('result')['postings'])

    def get_barcode_marketplace(
        self, name: str, order_id: str, prefix: str
    ) -> None:
        """Функция скачивает штрих-кода из магазина."""
        print(order_id)
        json = {
            "posting_number": [
                order_id
            ]
        }
        print(OZON_HEADERS, json)

        response = requests.post(
            'https://api-seller.ozon.ru/v2/posting/fbs/package-label',
            json=json,
            headers=OZON_HEADERS
        )
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(
                'Невозможно скачать штрих-код.',
                response.status_code
            )

        return self.write_down_barcode_file(
            name=name, order_id=order_id,
            prefix=prefix, response=response
        )

    def order_data_compose(self, order_list: dict) -> None:
        """Вытягивает данные из ответа API для доставки."""
        delivery_forms = []
        barcode_forms = []
        for order in order_list:
            items_list = []
            date_dost = order["shipment_date"][:10].replace('-', '.')
            for item in order['products']:
                items_list.append(self.item_form_validation(
                    amount=item['quantity'],
                    offer_id=str(item['offer_id'])
                ))
            delivery_forms += [
                super().delivery_form_validation(
                    order_number=('2P-' + str(order['posting_number'])),
                    date_dost=date_dost,
                    items_list=items_list
                )
            ]
            barcode_forms.append(
                self.get_barcode_marketplace(
                    name='ozon',
                    order_id=str(order['posting_number']),
                    prefix='2P-'
                )
            )

        return self.make_order(delivery_forms, barcode_forms)


def check_tokens() -> bool:
    """Проверка всех токенов на валидность."""
    return all((
        DELIVERY_PARTNER_ID, DELIVERY_KEY,
        OZON_TOKEN, OZON_ID,
        OZON_HEADERS, OZON_PARAMS,
        OZON_MATVEEVSKAYA_MARKETPLACE,
        YANDEX_CAMP_ID, YANDEX_TOKEN,
        YANDEX_CLIENT_ID, YANDEX_MARKETPLACE,
        YANDEX_HEADERS, YANDEX_PARAMS,
        BASE_YANDEX_URL, BASE_URL_DELIVERY,
        BARCODE_DELIVERY_URL, BASE_URL_OZON
    ))


def call_Yandex() -> None:
    """Функция обращения к YM API."""
    response = Yandex().market_place_request()
    order_pages = [Yandex().get_orders(response)]

    if (response['pager']['pagesCount']
            != response['pager']['currentPage']):

        while (response['pager']['pagesCount']
                == response['pager']['currentPage']):
            response = requests.get(
                url=BASE_YANDEX_URL,
                headers=YANDEX_HEADERS,
                params=YANDEX_PARAMS.update(
                    {'page': response['pager']['currentPage'] + 1}
                )
            )
            check_response = Yandex().get_orders(response)
            order_pages.append(check_response)

    for page in order_pages:
        Yandex().order_data_compose(page)


def call_ozon() -> None:
    """Функция обращения к OZON."""
    Ozon().market_place_request()


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
        filename=os.path.join(BASE_DIR, 'main.log'),
        filemode='w',
        format=(
            'line:%(lineno)s \n'
            'time:%(asctime)s \n'
            'status:%(levelname)s \n'
            'info:%(message)s \n')
    )

    if not check_tokens():
        logging.critical('Ошибка с инициализацией Токенов.')
        sys.exit('Ошибка, токены не заданы или заданы, но неправильно.')

    while True:
        try:
            clean_pdf()
            call_Yandex()
            logging.info('Заказы с Яндекс создались.')
            call_ozon()
            logging.info('Заказы с OZON создались.')
        except Exception as error:
            logging.error(error, traceback)


if __name__ == '__main__':
    main()
