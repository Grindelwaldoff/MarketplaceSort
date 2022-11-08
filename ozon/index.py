import os
import logging

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(__file__)

TOKEN = os.getenv('TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
KEY_NAME = os.getenv('KEY_NAME')


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

    while True:
        pass


if __name__ == '__main__':
    main()
