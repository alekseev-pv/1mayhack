import logging
import os
import sys

import requests
import telegram
from dotenv import load_dotenv
from http import HTTPStatus
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram import ReplyKeyboardMarkup
from params import TIMING, MENU, ALCOHOL, LOCATION

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
updater = Updater(token=TELEGRAM_TOKEN)


def get_timing(update, context):
    chat = update.effective_chat
    for key in TIMING:
        print(f'{key} - {TIMING[key]}')
        context.bot.send_message(
            chat_id=chat.id,
            text=f'{key} - {TIMING[key]}',
        )


def start_bot(update, context):
    chat = update.effective_chat
    # name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['Тайминг', 'Место проведения'],
                                  ['Меню', 'Алкогольное меню']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет! Добро пожаловать в Wedding Bot!',
        reply_markup=button
    )


def get_menu(update, context):
    chat = update.effective_chat
    for key in MENU:
        context.bot.send_message(
            chat_id=chat.id,
            text=key,
        )
        for i in MENU[key]:
            context.bot.send_message(
                chat_id=chat.id,
                text=i,
            )


def get_alcohol_menu(update, context):
    chat = update.effective_chat
    for key in ALCOHOL:
        context.bot.send_message(
            chat_id=chat.id,
            text=key,
        )


def get_location_info(update, context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=LOCATION,
    )


def admin_menu(update, context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=LOCATION,
    )


# def append_to_menu(update, context):
#     chat = update.effective_chat
#

updater.dispatcher.add_handler(CommandHandler('start', start_bot))
updater.dispatcher.add_handler(MessageHandler(Filters.text('Тайминг'), get_timing))
updater.dispatcher.add_handler(MessageHandler(Filters.text('Меню'), get_menu))
updater.dispatcher.add_handler(MessageHandler(Filters.text('Алкогольное меню'), get_alcohol_menu))
updater.dispatcher.add_handler(MessageHandler(Filters.text('Место проведения'), get_location_info))
# updater.dispatcher.add_handler(MessageHandler(Filters.text('Добавить блюдо в меню'), append_to_menu))


updater.start_polling()
updater.idle()


# if __name__ == '__main__':
#     pass