import os
import logging
from datetime import datetime as dt, timedelta
from http import HTTPStatus
import base64
import sys
import time

import requests
from telegram import Bot, TelegramError

from constants.data import (
    DELIVERY_PARTNER_ID, DELIVERY_KEY,
    OZON_TOKEN, OZON_ID,
    OZON_HEADERS, OZON_PARAMS,
    OZON_MATVEEVSKAYA_MARKETPLACE,
    YANDEX_CAMP_ID, YANDEX_TOKEN,
    YANDEX_CLIENT_ID, YANDEX_MARKETPLACE,
    YANDEX_HEADERS, YANDEX_PARAMS,
    TELEGRAM_CHAT_ID, TELEGRAM_TOKEN,
    CHECK_HOUR, OZON_ID_2, OZON_TOKEN_2,
    OZON_HEADERS_2, TELEGRAM_TOKEN_2,
)
from constants.urls import (
    BASE_YANDEX_URL, BASE_URL_DELIVERY,
    BARCODE_DELIVERY_URL, BASE_URL_OZON
)
import acts
import barcodes


OZON_BAR_LIST_K = {}
OZON_BAR_LIST_2P = {}
YANDEX_BAR_LIST = {}

OZON_ACTS_DATA_K = {}
OZON_ACTS_DATA_2P = {}
YANDEX_ACTS_DATA = {}

BASE_DIR = os.path.dirname(__file__)

BOT = Bot(token=TELEGRAM_TOKEN)
BOT_FOR_LOGS = Bot(token=TELEGRAM_TOKEN_2)


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
            "name": self.get_product_name(offer_id),
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

    def get_product_name(self, offer_id):
        """Берет наименование из каталога склада."""
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
                if item['article'] == offer_id:
                    return item['name']
        except Exception as error:
            raise Exception(error)

    def delivery_form_validation(
        self, order_number: str,
        date_dost: str, items_list: list,
        marketplace_code: str
    ) -> dict:
        """Формирует запрос для GURU."""
        order_form = {
            "partner_id": DELIVERY_PARTNER_ID,
            "key": DELIVERY_KEY,
            "order_number": order_number,
            "usluga": "ДОСТАВКА",
            "marketplace_id": marketplace_code,
            "sposob_dostavki": "Маркетплейс",
            "tip_otpr": "FBS с комплектацией",
            "cont_name": "Батыр",
            "cont_tel": "+7(964)775-52-25",
            "cont_mail": "bibalaev@gmail.com",
            "region_iz": "Москва",
            "ocen_sum": 100,
            "free_date": "1",
            "date_dost": date_dost
        }
        order_form.update({"products": items_list})

        return order_form

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

    def json_barcode_to_delivery_form(
        self, name, order_id: str, prefix: str, folder: str
    ) -> dict:
        """Подготавливает запрос к API склада для отправки штрихкода."""
        with open(f'./{name}/{folder}/{order_id}.pdf', 'rb') as file:
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

    def send_request_to_shipment(
        self, delivery_forms: list,
        barcode_list: list, marketplace: str,
        prefix: str
    ) -> None:
        """Отправляет запрос к API Склада, создает заявку на доставку."""
        stat_list = []
        for form in delivery_forms:
            response = requests.post(
                BASE_URL_DELIVERY,
                json=form,
            )
            if response.status_code != HTTPStatus.OK:
                raise ConnectionError(
                    'Запрос к API склада не увенчался успехом.'
                )
            else:
                print(response.json())
                if 'errors' in response.json():
                    print(form['order_number'])
                    barcode_list.remove(str(form['order_number']))
                else:
                    stat_list.append(form)

        if prefix == 'Y-' and barcode_list != []:
            YANDEX_BAR_LIST.update({
                "barcode_list": barcode_list,
                "marketplace": marketplace,
                "prefix": prefix,
                "stat_list": self.get_order_list_for_tg(stat_list)
            })
        if prefix == '2P-' and barcode_list != []:
            OZON_BAR_LIST_2P.update({
                "barcode_list": barcode_list,
                "marketplace": marketplace,
                "prefix": prefix,
                "stat_list": self.get_order_list_for_tg(stat_list)
            })
        if prefix == 'K-' and barcode_list != []:
            OZON_BAR_LIST_K.update({
                "barcode_list": barcode_list,
                "marketplace": marketplace,
                "prefix": prefix,
                "stat_list": self.get_order_list_for_tg(stat_list)
            })

    def tg_date_format(self, date: str) -> str:
        """Меняет формат даты для тг бота."""
        res = dt.strptime(date, "%Y.%m.%d")
        return res.date().strftime('%d.%m.%Y')

    def get_order_list_for_tg(self, delivery_forms: list) -> str:
        """Берет нужные данные и отпраляет лог в тг."""
        result = ''
        for order in delivery_forms:
            result += (f'{self.tg_date_format(order["date_dost"])}'
                       f' / {order["order_number"]}')
            for item in order['products']:
                result += f' / {item["code"]} / {item["qty"]} шт '
            result += ' \n'
        return result


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
                'Запрос к API Yandex не увенчался успехом.'
            )

        if not response.json():
            raise requests.JSONDecodeError(
                'Не удается преобразовать ответ API Yandex в JSON.'
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

    def date_valid(self, data) -> str:
        """Меняет формат даты, который вернул API."""
        result = data[6::] + '.' + data[3:5] + '.' + data[:2]
        return str(result)

    def order_data_compose(
        self,
        page_list: list
    ) -> None:
        """Вытягивает данные из ответа API для доставки."""
        delivery_forms = []
        barcode_list = []
        tommorow = (dt.today() + timedelta(days=1)).strftime('%d-%m-%Y')
        for order in page_list:
            items_list = []
            date_dost = self.date_valid(
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
                    items_list=items_list,
                    marketplace_code=YANDEX_MARKETPLACE
                )
            ]
            barcode_list.append(
                'Y-' + str(order['id'])
            )

        self.send_request_to_shipment(
            delivery_forms=delivery_forms,
            barcode_list=barcode_list,
            marketplace='Yandex',
            prefix='Y-'
        )

        for order in page_list:
            try:
                if (
                    tommorow in order['delivery']['shipments']
                    [0]['shipmentDate']
                ):
                    YANDEX_ACTS_DATA.update({
                        "order_id": order['id']
                    })
                    break
            except Exception as error:
                raise ConnectionError(
                    'Не удалось загрузить акт в сервис доставки. \n',
                    order['id'],
                    f'{error}'
                )


class Ozon(MakeOrdersForGuru):
    """Класс для получения заказов с OZON."""

    def market_place_request(self, prefix: str) -> dict:
        """Обращение к  API OZON."""
        if prefix == '2P-':
            headers = OZON_HEADERS
        else:
            headers = OZON_HEADERS_2

        response = requests.post(
            url=BASE_URL_OZON,
            headers=headers,
            json=OZON_PARAMS
        )
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError('Запрос к API Ozon не увенчался успехом.')

        return self.get_orders(response.json(), prefix)

    def get_orders(self, response: dict, prefix: str) -> list:
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

        return self.order_data_compose(
            response.get('result')['postings'],
            prefix=prefix
        )

    def order_data_compose(self, order_list: dict, prefix: str) -> None:
        """Вытягивает данные из ответа API для доставки."""
        delivery_forms = []
        barcode_list = []
        tommorow = (dt.today() + timedelta(days=1)).strftime('%Y-%m-%d')
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
                    order_number=(prefix + str(order['posting_number'])),
                    date_dost=date_dost,
                    items_list=items_list,
                    marketplace_code=OZON_MATVEEVSKAYA_MARKETPLACE
                )
            ]
            barcode_list.append(
                prefix + str(order['posting_number'])
            )

        self.send_request_to_shipment(
            delivery_forms=delivery_forms,
            barcode_list=barcode_list,
            marketplace='Ozon',
            prefix=prefix
        )

        for order in order_list:
            if tommorow in order['shipment_date']:
                if prefix == '2P-':
                    OZON_ACTS_DATA_2P.update({
                            "delivery_id": order['delivery_method'].get('id'),
                            "prefix": prefix,
                            "date": str(
                                (
                                    dt.utcnow() + timedelta(hours=23)
                                ).isoformat()+'Z'
                            ),
                            "order_id": order['posting_number']
                        })
                else:
                    OZON_ACTS_DATA_K.update({
                            "delivery_id": order['delivery_method'].get('id'),
                            "prefix": prefix,
                            "date": str(
                                (
                                    dt.utcnow() + timedelta(hours=23)
                                ).isoformat()+'Z'
                            ),
                            "order_id": order['posting_number']
                        })
                break


def send_message(bot, message) -> None:
    """Отправляет сообщение в ТГ."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
    except TelegramError:
        raise TelegramError('Ошибка в заимодействии с API ТГ.')
    else:
        logging.info('Сообщение отправлено.')


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
        BARCODE_DELIVERY_URL, BASE_URL_OZON,
        TELEGRAM_CHAT_ID, TELEGRAM_TOKEN,
        CHECK_HOUR, OZON_ID_2, OZON_TOKEN_2,
        OZON_HEADERS_2
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


def clean_pdf() -> None:
    """Очищает все штрих кода по завершению."""
    dirs = ['./yandex/pdf', './ozon/pdf']
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
        sys.exit('Ошибка, токены не заданы или заданы неправильно.')

    try:
        send_message(
            BOT,
            message=f'''
            ----------------{dt.now().strftime('%d.%m.%Y')}----------------
            '''
        )
        send_message(
            BOT_FOR_LOGS,
            message=f'''
            ----------------{dt.now().strftime('%d.%m.%Y')}----------------
            '''
        )
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        call_Yandex()
        logging.info('Заказы с Яндекс создались.')
        send_message(
            BOT,
            f'Акт будет загружен в заказ под номером Y-{ + YANDEX_ACTS_DATA["order_id"]}'
        )
        clean_pdf()
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        Ozon().market_place_request(prefix='2P-')
        logging.info('Заказы с OZON создались.')
        clean_pdf()
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        Ozon().market_place_request(prefix='K-')
        logging.info('Заказы с OZON создались.')
        clean_pdf()
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        time.sleep(10)
        print(OZON_BAR_LIST_K)
        print(len(OZON_BAR_LIST_K["stat_list"]))
        barcodes.Barcode().download(
            barcode_list=OZON_BAR_LIST_K['barcode_list'],
            marketplace=OZON_BAR_LIST_K['marketplace'],
            prefix=OZON_BAR_LIST_K['prefix'],
        )
        message = (
            f'{OZON_BAR_LIST_K["marketplace"]} обработано {len(OZON_BAR_LIST_K["barcode_list"])} заказов: \n'
            + OZON_BAR_LIST_K["stat_list"]
        )
        send_message(BOT, message=message)
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        time.sleep(10)
        barcodes.Barcode().download(
            barcode_list=YANDEX_BAR_LIST['barcode_list'],
            marketplace=YANDEX_BAR_LIST['marketplace'],
            prefix=YANDEX_BAR_LIST['prefix'],
        )
        message = (
            f'{YANDEX_BAR_LIST["marketplace"]} обработано {len(YANDEX_BAR_LIST["barcode_list"])} заказов: \n'
            + YANDEX_BAR_LIST["stat_list"]
        )
        send_message(BOT, message=message)
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        time.sleep(10)
        print(OZON_BAR_LIST_2P)
        barcodes.Barcode().download(
            barcode_list=OZON_BAR_LIST_2P['barcode_list'],
            marketplace=OZON_BAR_LIST_2P['marketplace'],
            prefix=OZON_BAR_LIST_2P['prefix'],
        )
        message = (
            f'{OZON_BAR_LIST_2P["marketplace"]} обработано {len(OZON_BAR_LIST_2P["barcode_list"])} заказов: \n'
            + OZON_BAR_LIST_2P["stat_list"]
        )
        send_message(BOT, message=message)
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        time.sleep(10)
        acts.YandexActs().download(
            order_id=YANDEX_ACTS_DATA["order_id"]
        )
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        print(OZON_ACTS_DATA_2P)
        acts.OzonActs().download(
            delivery_id=OZON_ACTS_DATA_2P["delivery_id"],
            prefix=OZON_ACTS_DATA_2P["prefix"],
            date=str(
                (dt.utcnow() + timedelta(hours=23)).isoformat()+'Z'
            ),
            order_id=OZON_ACTS_DATA_2P["order_id"]
        )
        send_message(
            BOT,
            'Акты прикреплены в '
            f'{OZON_ACTS_DATA_2P["prefix"] + OZON_ACTS_DATA_2P["order_id"]}'
        )
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    try:
        print(OZON_ACTS_DATA_K)
        acts.OzonActs().download(
            delivery_id=OZON_ACTS_DATA_K["delivery_id"],
            prefix=OZON_ACTS_DATA_K["prefix"],
            date=str(
                (dt.utcnow() + timedelta(hours=23)).isoformat()+'Z'
            ),
            order_id=OZON_ACTS_DATA_K["order_id"]
        )
        send_message(
            BOT,
            'Акты прикреплены в '
            f'{OZON_ACTS_DATA_K["prefix"] + OZON_ACTS_DATA_K["order_id"]}'
        )
    except Exception as error:
        logging.error(error)
        send_message(BOT_FOR_LOGS, str(error))

    send_message(BOT, message='Обработка завершена')

    clean_pdf()


if __name__ == '__main__':
    main()
