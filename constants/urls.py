import os

from dotenv import load_dotenv


load_dotenv()


BASE_YANDEX_URL = ('https://api.partner.market.yandex.ru/v2'
                   f'/campaigns/{os.getenv("YANDEX_CAMPAIGN_ID")}/orders.json')
BASE_URL_DELIVERY = ('https://api.dostavka.guru/client'
                     '/in_up_market.php?json=yes')
BARCODE_DELIVERY_URL = 'https://api.dostavka.guru/methods/files/'

BASE_URL_OZON = 'https://api-seller.ozon.ru/v3/posting/fbs/list'
