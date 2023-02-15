import requests
from http import HTTPStatus
import time


from constants.data import (
    OZON_HEADERS,
    YANDEX_HEADERS,
    OZON_HEADERS_2
)
from constants.urls import (
    OZON_ACTS, OZON_WAYBILL,
    YANDEX_ACTS, OZON_ACTS_CREATE
)
from barcodes import Barcode, MakeOrdersForGuru


class YandexActs():
    """Класс работающий с актами Yandex."""

    def download(
        self,
        order_id: int
    ) -> None:
        response = requests.get(
            YANDEX_ACTS,
            headers=YANDEX_HEADERS,
        )
        print(response.status_code, order_id)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(
                'Невозможно скачать акт из Yandex.',
                response.json()
            )
        with open(f'./yandex/acts/{order_id}.pdf', 'wb') as file:
            file.write(response._content)

        download_form = MakeOrdersForGuru().json_barcode_to_delivery_form(
            folder='acts',
            name='yandex',
            order_id=str(order_id),
            prefix='Y-'
        )

        return Barcode().send_barcode(
            download_form
        )


class OzonActs():
    """Класс работающий с OZON актами."""

    def download(
        self, delivery_id: int,
        prefix: str, date: str, order_id: int
    ) -> None:
        if prefix == '2P-':
            headers = OZON_HEADERS
        else:
            headers = OZON_HEADERS_2

        json = {
            "delivery_method_id": delivery_id,
            "departure_date": date
        }
        response = requests.post(
            OZON_ACTS_CREATE,
            json=json,
            headers=headers
        )
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(
                'На данную отгрузку нельзя скачать акт.',
                delivery_id
            )
        time.sleep(60)
        self.send_act(
            id=response.json().get('result')['id'],
            headers=headers,
            order_id=order_id,
            prefix=prefix
        )
        self.send_waybill(
            id=response.json().get('result')['id'],
            headers=headers,
            order_id=order_id,
            prefix=prefix
        )

    def send_waybill(
        self, id: int, headers: dict,
        order_id: str, prefix: str
    ) -> None:
        response = requests.post(
            OZON_WAYBILL,
            json={
                'id': id
            },
            headers=headers
        )
        print(response.status_code, order_id)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(
                'Невозможно скачать накладную.',
                response.status_code, order_id
            )
        with open(f'./ozon/waybills/{order_id}.pdf', 'wb') as file:
            file.write(response._content)

        waybill_form = MakeOrdersForGuru().json_barcode_to_delivery_form(
            folder='waybills',
            name='ozon',
            order_id=order_id,
            prefix=prefix
        )

        return Barcode().send_barcode(waybill_form)

    def send_act(
        self, id: int, headers: dict,
        prefix: str, order_id: str
    ) -> None:
        json = {
            "id": id,
            "doc_type": "act_of_acceptance"
        }
        response = requests.post(
            OZON_ACTS, json=json, headers=headers
        )
        print(response.status_code, order_id)
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError(
                'Невозможно скачать акт.',
                response.status_code, order_id
            )
        with open(f'./ozon/acts/{order_id}.pdf', 'wb') as file:
            file.write(response._content)

        act_form = MakeOrdersForGuru().json_barcode_to_delivery_form(
            folder='acts',
            name='ozon',
            order_id=order_id,
            prefix=prefix
        )

        return Barcode().send_barcode(act_form)
