import os

from dotenv import load_dotenv


load_dotenv()

DELIVERY_PARTNER_ID = os.getenv('DELIVERY_ID')
DELIVERY_KEY = os.getenv('DELIVERY_TOKEN')

OZON_TOKEN = os.getenv('OZON_TOKEN')
OZON_ID = os.getenv('OZON_ID')
OZON_MATVEEVSKAYA_MARKETPLACE = os.getenv('OZON_MARKETPLACE')

OZON_HEADERS = {
    'Client-Id': OZON_ID,
    'Api-Key': OZON_TOKEN,
    'Content-Type': 'application/json'
}

OZON_PARAMS = {
        "dir": "ASC",
        "filter":
        {
            "since": "",
            "status": "awaiting_deliver",
            "to": ""
        },
        "limit": 100,
        "offset": 0
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
