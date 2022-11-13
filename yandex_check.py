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

url = f'https://api.partner.market.yandex.ru/v2/campaigns/{YANDEX_CAMP_ID}/orders/{154559839}.json'
response = requests.get(url, headers=YANDEX_HEADERS)
print(response.json())

dt.utcnow().strftime('%Y.%m.%d')