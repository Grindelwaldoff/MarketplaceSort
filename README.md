# Marketplace orders (OZON, YANDEX)
### Описание
Составляет заказы для гуру из маркетплейсов и отпраляет результаты в тг.

### Технологии
Python 3.10
python-telegram-bot 13.7


### Запуск проекта в dev-режиме
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- Создайте в основной папке файл .env со всеми токенами
```
DELIVERY_ID - id guru
DELIVERY_TOKEN - token guru
YANDEX_TOKEN - yandex oauth token
YANDEX_ID - yandex oauth client id
OZON_TOKEN - ozon api token
OZON_ID - ozon profile id
OZON_TOKEN_2 - ozon api token для воторого кабинета
OZON_ID_2 - ozon profile id для вторго кабинета
OZON_MARKETPLACE - код склада ozon в системе Guru
YANDEX_MARKETPLACE - код склада Yandex в системе Guru
YANDEX_CAMPAIGN_ID - id компании клиента без '11-'
CHAT_ID - chat id клиента
TELEGRAM_TOKEN - token бота клиента
```
- В основной папке выполните команду:
```
python3 index.py
```
### Автор
Grindelwaldoff