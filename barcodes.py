from http import HTTPStatus
import requests

from constants.data import (
    OZON_HEADERS, OZON_HEADERS_2,
    YANDEX_CAMP_ID, YANDEX_HEADERS
)
from constants.urls import BARCODE_DELIVERY_URL
from index import MakeOrdersForGuru


class Barcode():
    """Класс работающий со штрих-кодами."""

    def download(
        self, barcode_list: list,
        marketplace: str, prefix: str
    ) -> None:
        """Функция скачивает штрих-кода из магазина."""
        for order_id in barcode_list:
            order_id = order_id[len(prefix)::]
            if marketplace == 'Yandex':
                url = (
                    'https://api.partner.market.yandex.ru/v2/campaigns'
                    f'/{YANDEX_CAMP_ID}/orders/{order_id}/delivery/labels'
                )

                response = requests.get(url, headers=YANDEX_HEADERS)
                with open(f'./yandex/pdf/{order_id}.pdf', 'wb') as file:
                    file.write(response._content)

                barcode_form = MakeOrdersForGuru(
                ).json_barcode_to_delivery_form(
                    folder='pdf',
                    name='yandex', order_id=order_id, prefix=prefix
                )

                self.send_barcode(barcode_form=barcode_form)

            if marketplace == 'Ozon':
                if prefix == '2P-':
                    headers = OZON_HEADERS
                else:
                    headers = OZON_HEADERS_2

                json = {
                    "posting_number": [order_id]
                }

                response = requests.post(
                    'https://api-seller.ozon.ru/v2/posting/fbs/package-label',
                    json=json,
                    headers=headers
                )
                if response.status_code != HTTPStatus.OK:
                    raise ConnectionError(
                        'Невозможно скачать штрих-код.',
                        response.json()
                    )

                with open(f'./ozon/pdf/{order_id}.pdf', 'wb') as file:
                    file.write(response._content)

                barcode_form = MakeOrdersForGuru(
                ).json_barcode_to_delivery_form(
                    folder='pdf',
                    name='ozon', order_id=order_id, prefix=prefix
                )

                self.send_barcode(barcode_form=barcode_form)

    def send_barcode(self, barcode_form: dict) -> None:
        """Отправляет штрих-кода на склад."""
        response = requests.post(
            BARCODE_DELIVERY_URL,
            json=barcode_form,
        )

        print(response.json())
