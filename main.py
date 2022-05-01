import logging
import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

load_dotenv()

secret_token = os.getenv('TOKEN')
secret_url = os.getenv('URL')
another_url = os.getenv('ANOTHER_URL')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def get_new_image():
    try:
        response = requests.get(secret_url)
    except Exception as error:
        print(error)
        new_url = another_url
        response = requests.get(new_url)
    response = response.json()
    return response.get('url')


def get_day_expln():
    response = requests.get(secret_url)
    answer = response.json()
    return answer.get('explanation')


def hello_user(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/start']], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text='Hi, {}. Picture day by NASA'.format(name),
        reply_markup=button
    )
    context.bot.send_photo(chat.id, get_new_image())
    context.bot.send_message(chat.id, get_day_expln())


def main():
    updater = Updater(token=secret_token)
    updater.dispatcher.add_handler(CommandHandler('start', hello_user))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
