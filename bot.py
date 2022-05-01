import logging
import os
import random

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

load_dotenv()

updater = Updater(os.getenv('TOKEN'))

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='homework.log',
    filemode='a'
)


def say_hi(update, context):
    chat = update.effective_chat
    text = ('Привет, я фанат сериала "Во все тяжкие" и знаю все цитаты'
            ' Хайзенберга и Джесси, спрашивай любую!')
    button = ReplyKeyboardMarkup(
        [['Скажи цитату Хайзенберга'],
         ['Скажи цитату Джесси Пинкмана']],
        resize_keyboard=True)
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=button
        )
    except Exception as error:
        logging.error(f'Приветствие не отправлено, {error}')


def true(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup(
        [['Назад']],
        resize_keyboard=True)
    text = ('Я истинный фанат, знаю только в оригинале.'
            ' Но если очень хочется, воспользуйся переводчиком.'
            ' Вот <a href="https://translate.google.ru/">ссылка</a>')
    try:
        context.bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=button,
            parse_mode=ParseMode.HTML
        )
    except Exception as error:
        logging.error(f'Ответ на вопрос не получен, {error}')


def go_back(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup(
        [['Скажи цитату Хайзенберга'],
         ['Скажи цитату Джесси Пинкмана']],
        resize_keyboard=True)
    try:
        context.bot.send_message(
            text='Выбери героя',
            chat_id=chat.id,
            reply_markup=button
        )
    except Exception as error:
        logging.error(f'Основное меню недоступно, {error}')


def get_quote(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['Назад'],
         ['А по-русски?']],
        resize_keyboard=True
    )
    if update['message']['text'] == 'Скажи цитату Хайзенберга':
        try:
            author = 'Walter+White'
            response = requests.get(
                f'https://www.breakingbadapi.com/api/quote?author={author}'
            )
            response = response.json()
            odd_choice = random.choice(response)
            quote = odd_choice.get('quote')
            context.bot.send_message(
                chat_id=chat.id,
                text='Лови фразочку {}.'.format(name) + f' {quote}',
                reply_markup=button
            )
        except Exception as error:
            logging.error(f'API не работает, {error}')
    else:
        try:
            author = 'Jesse+Pinkman'
            response = requests.get(
                f'https://www.breakingbadapi.com/api/quote?author={author}'
            )
            response = response.json()
            odd_choice = random.choice(response)
            quote = odd_choice.get('quote')
            context.bot.send_message(
                chat_id=chat.id,
                text='Лови фразочку {}.'.format(name) + f' {quote}',
                reply_markup=button
            )
        except Exception as error:
            logging.error(f'API не работает, {error}')


def main():
    updater.dispatcher.add_handler(CommandHandler('start', say_hi))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Назад'), go_back))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Скажи цитату Хайзенберга'), get_quote))
    updater.dispatcher.add_handler(
        MessageHandler(
            Filters.text('Скажи цитату Джесси Пинкмана'), get_quote))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('А по-русски?'), true))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
