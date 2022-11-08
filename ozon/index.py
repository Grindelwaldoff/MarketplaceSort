import os
import json
import logging
import time
from datetime import datetime as dt

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(__file__)

TOKEN = os.getenv('TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
HEADERS = {
    'Client-Id': CLIENT_ID,
    'Api-Key': TOKEN,
    'Content-Type': 'application/json'
}

BASE_URL_OZON = 'https://api-seller.ozon.ru/v3/posting/fbs/list'


def get_list_request_ozon(current_date: str) -> dict:
    params = {
        "dir": "ASC",
        "filter": {
            "cutoff_from": "2021-08-24T14:15:22Z",
            "cutoff_to": current_date,
            "delivery_method_id": [],
            "provider_id": [],
            "status": "awaiting_packaging",
            "warehouse_id": []
        },
        "limit": 100,
        "offset": 0
    }
    response = requests.post(url=BASE_URL_OZON, headers=HEADERS, json=params)
    res = json.loads(response._content)
    print(res)
    return res


def main():
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

    current_date = str(dt.utcnow().isoformat()+'Z')

    while True:
        check_time = dt.now().hour
        print(check_time)
        try:
            ozon_list = get_list_request_ozon(current_date)
            break
        except Exception as error:
            logging.error(error)
        else:
            break


if __name__ == '__main__':
    main()
