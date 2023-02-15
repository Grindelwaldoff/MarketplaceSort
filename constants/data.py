import os
from datetime import datetime as dt, timedelta

from dotenv import load_dotenv


load_dotenv()

CHECK_HOUR = 13

DELIVERY_PARTNER_ID = os.getenv('DELIVERY_ID')
DELIVERY_KEY = os.getenv('DELIVERY_TOKEN')

OZON_TOKEN = os.getenv('OZON_TOKEN')
OZON_ID = os.getenv('OZON_ID')
OZON_TOKEN_2 = os.getenv('OZON_TOKEN_2')
OZON_ID_2 = os.getenv('OZON_ID_2')
OZON_MATVEEVSKAYA_MARKETPLACE = os.getenv('OZON_MARKETPLACE')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_TOKEN_2 = os.getenv('TELEGRAM_TOKEN_2')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

OZON_HEADERS = {
    'Client-Id': OZON_ID,
    'Api-Key': OZON_TOKEN,
    'Content-Type': 'application/json'
}

OZON_HEADERS_2 = {
    'Client-Id': OZON_ID_2,
    'Api-Key': OZON_TOKEN_2,
    'Content-Type': 'application/json'
}

current_date = str(dt.utcnow().isoformat()+'Z')

OZON_PARAMS = {
        'dir': 'ASC',
        'filter':
        {
            'since': str((
                dt.utcnow() - timedelta(days=7)).isoformat()
            ) + 'Z',
            'status': 'awaiting_deliver',
            'to': current_date
        },
        'limit': 100,
        'offset': 0
    }

YANDEX_CAMP_ID = os.getenv('YANDEX_CAMPAIGN_ID')
YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
YANDEX_CLIENT_ID = os.getenv('YANDEX_ID')
YANDEX_MARKETPLACE = os.getenv('YANDEX_MARKETPLACE')

YANDEX_PARAMS = {
    'status': 'PROCESSING',
    'substatus': 'READY_TO_SHIP',
    'page': 1
}

YANDEX_HEADERS = {
    'Authorization': (f'OAuth oauth_token={YANDEX_TOKEN},'
                      f'oauth_client_id={YANDEX_CLIENT_ID}'),
    'Content-Type': 'application/json;charset=utf-8'
}

WB_HEADERS = {
    'Authorization': os.getenv('WB_TOKEN'),
    'Content-Type': 'application/json'
}

SBER_HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'
}

SBER_PARAMS_GET = {
    "meta": {},
    "data": {
        "token": os.getenv('SBER_TOKEN'),
        "shipments": [
        ]
    }
}

SBER_PARAMS_SEARCH = {
    "data": {
        "token": os.getenv('SBER_TOKEN'),
        "dateFrom": "2021-04-17T21:00:00Z",
        "dateTo": "2021-05-19T20:59:59Z",
        "count": 10,
        "statuses": [
            "CONFIRMED",
        ]
    },
    "meta": {}
}

main_order_form = {
    'partner_id': DELIVERY_PARTNER_ID,
    'key': DELIVERY_KEY,
    'order_number': '',
    'usluga': 'ДОСТАВКА',
    'marketplace_id': '',
    'sposob_dostavki': 'Маркетплейс',
    'tip_otpr': 'FBS с комплектацией',
    'cont_name': 'Батыр',
    'cont_tel': '+7(964)775-52-25',
    'cont_mail': 'bibalaev@gmail.com',
    'region_iz': 'Москва',
    'ocen_sum': 100,
    'free_date': '0',
    'date_dost': '',
    'products': []
}

item_form = {
    'name': 'Товар',
    'qty': '',
    'ed': 'шт',
    'code': '',
    'oc': 100,
    'bare': '',
    'mono': 0,
    'mark': 0,
    'pack': 0
}

barcode_form = {
    "partner_id": DELIVERY_PARTNER_ID,
    "key": DELIVERY_KEY,
    "format": "pdf",
    "type": 0,
    "copy": 1,
    "name": ".pdf",
    "order_number": "",
    "file": ""
}
