import os

from dotenv import load_dotenv


load_dotenv()

DELIVERY_PARTNER_ID = os.getenv('DELIVERY_ID')
DELIVERY_KEY = os.getenv('DELIVERY_TOKEN')

OZON_TOKEN = os.getenv('OZON_TOKEN')
OZON_ID = os.getenv('OZON_ID')
OZON_MATVEEVSKAYA_MARKETPLACE = os.getenv('OZON_MARKETPLACE')

YANDEX_CAMP_ID = os.getenv('YANDEX_CAMPAIGN_ID')
YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
YANDEX_CLIENT_ID = os.getenv('YANDEX_ID')
YANDEX_MARKETPLACE = os.getenv('YANDEX_MARKETPLACE')
