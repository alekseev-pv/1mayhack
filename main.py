import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram import ReplyKeyboardMarkup

import logging
import requests

import os
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_YANDEX_IMAGE = 'https://yandex.ru/images/search?source=collections' \
                      '&rpt=imageview&url=urltofile&'




def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Бот телеги отправил сообщение {message} ')
    except Exception as error:
        logging.error(f'Сбой в работе бота телеги: {error}')

def get_new_text():
    return f'Просто новый текст'

def new_text(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat.id, get_new_text())


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/newtext']], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}. Посмотри на текст, которого я для тебя нашел',
        reply_markup=button
    )

def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newtext', new_text))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

