import telegram
from telegram.ext import Updater
import logging
import requests

import os
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ENDPOIT_YANDEX_IMAGE = 'https://yandex.ru/images/search?source=collections' \
                      '&rpt=imageview&url=urltofile&'


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Бот телеги отправил сообщение {message} ')
    except Exception as error:
        logging.error(f'Сбой в работе бота телеги: {error}')

if __name__ == '__main__':
    send_message(bot, f'Отправка первого сообщения из программы')

