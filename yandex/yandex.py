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

BASE_YANDEX_URL = ('https://api.partner.market.yandex.ru/v2'
                   f'/campaigns/{os.getenv("CAMPAIGN_ID")}/orders.json')


