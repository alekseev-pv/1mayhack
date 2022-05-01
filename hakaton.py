import datetime
import os

import requests
import telegram.ext as tg
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup

from settings import HOROSCOPE_URL, ZODIAC, daily

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FIRST_MESSAGE = datetime.time(hour=9, minute=0, second=0, tzinfo=None)
USER_BASE = {}
LAST_ENTRY = {}


def parser(url = daily):
    """Парсинг страниц с гороскопами."""
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    allhoroscope = soup.findAll('div', class_='_2j-zP _1ylC5')
    text = [i.text for i in allhoroscope]
    horoscope = dict(zip(ZODIAC, text))
    return horoscope


def wake_up(update, context):
    """Стартовое сообщение."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['Овен', 'Телец', 'Близнецы', ],
                                  ['Рак', 'Лев', 'Дева', 'Весы', ],
                                  ['Скорпион', 'Стрелец', ],
                                  ['Козерог', 'Водолей', 'Рыбы']],
                                  resize_keyboard=True)
    if chat.id not in USER_BASE:
        context.bot.send_message(chat_id=chat.id,
                                 text=f'Привет, {name}. Кто ты по знаку '
                                      f'зодиака?', reply_markup=button)
    else:
        context.bot.send_message(chat_id=chat.id,
                                 text='Про кого тебе ещё рассказать?',
                                 reply_markup=button)


def user_text(update, context):
    """Выбор гороскопа."""
    zodiac = update.message.text
    chat_id = update.message.chat.id
    if chat_id not in USER_BASE.keys():
        USER_BASE[chat_id] = zodiac
    LAST_ENTRY[chat_id] = zodiac
    button = ReplyKeyboardMarkup([['На сегодня', 'На завтра'], ['На неделю'],
                                  ['Вернуться к знакам']],
                                resize_keyboard=True)
    context.bot.send_message(chat_id, f'Отлично, сейчас я тебе расскажу что '
                                      f'ждёт представителей знака зодиака '
                                      f'"{zodiac}". \n Какой гороскоп ты бы '
                                      f'хотел узнать?',
                             reply_markup=button)


def horoscope(update, context):
    """Отправка гороскопа."""
    horoscope = update.message.text
    url = HOROSCOPE_URL[horoscope]
    chat_id = update.message.chat.id
    zodiac = LAST_ENTRY[chat_id]
    text = parser(url)[zodiac]
    context.bot.send_message(chat_id, f'Гороскоп для {zodiac}\n {text}')


def error(update, context):
    """Обработка сообщений на которых нет ответа."""
    chat_id = update.message.chat.id
    text = 'Я не понимаю тебя. Воспользуйся кнопками.'
    context.bot.send_message(chat_id, text)


def callback_minute(context: tg.CallbackContext):
    """Ежедневная отправка гороскопа на сегодня."""
    for id in USER_BASE.keys():
        text = parser()[USER_BASE[id]]
        message = f'Гороскоп на сегодня, специально для {USER_BASE[id]}ов. ' \
                  f'\n {text} '
        context.bot.send_message(chat_id=id, text=message)


def main():
    """Основная логика."""
    updater = tg.Updater(token=TELEGRAM_TOKEN, use_context=True)
    updater.job_queue.run_repeating(callback_minute, interval=86400,
                                    first=FIRST_MESSAGE)
    updater.dispatcher.add_handler(tg.CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(tg.MessageHandler(tg.Filters.text(ZODIAC),
                                                     user_text))
    updater.dispatcher.add_handler(tg.MessageHandler(
        tg.Filters.text(HOROSCOPE_URL.keys()), horoscope))
    updater.dispatcher.add_handler(tg.MessageHandler(
        tg.Filters.text('Вернуться к знакам'), wake_up))
    updater.dispatcher.add_handler(tg.MessageHandler(tg.Filters.text, error))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
