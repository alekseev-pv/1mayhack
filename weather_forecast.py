import logging
import os
import sys
from http import HTTPStatus
from logging import StreamHandler

import requests
import telegram
from dotenv import load_dotenv
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

import exceptions
from constants import CONDITION, ENDPOINT, FORECAST_DAYS, WIND_DIR

load_dotenv()


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')

logger = logging.getLogger(__name__)


def send_message(bot: telegram.Bot, message: str) -> None:
    """Посылает сообщение в telegram, в случае ошибки и успеха логирует."""
    try:
        buttons = [[
            InlineKeyboardButton('Через 2 часа', callback_data='2'),
            InlineKeyboardButton('Через 6 часов', callback_data='6'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons, resize_keyboard=True)
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except telegram.error.TelegramError:
        logger.error(f'Бот не смог отправить сообщение "{message}"')
    else:
        logger.info(f'Бот отправил сообщение "{message}"')


def get_api_answer(lat: float, lon: float) -> dict:
    """Запрашивает endpoint, в случае ошибки бросает EndPointException."""
    HEADERS = {
        'X-Yandex-API-Key': YANDEX_API_KEY
    }
    params = {'lat': lat, 'lon': lon, 'limit': FORECAST_DAYS, 'hours': True}

    logger.debug('Запрос к эндпоинту.')
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.ConnectionError as error:
        raise exceptions.EndPointException('Сбой в работе программы: ' + error)
    if response.status_code != HTTPStatus.OK:
        raise exceptions.EndPointException(
            'Эндпоинт'
            '  https://api.weather.yandex.ru/v1/informers/'
            f' недоступен. Параметры запроса: {params}. Код ответа API:'
            f' {response.status_code}. Текст ответа: {response.text}'
        )
    return response.json()


def parse_weather(response: requests.Response) -> str:
    """
    Извлекает из информации о погоде
    """
    message = (
        f' <b><i>{CONDITION[response["fact"]["condition"]].capitalize()}'
        '</i></b>'
        f'\nТемпература: {response["fact"]["temp"]} C'
        f'\nДавление: {response["fact"]["pressure_mm"]} мм рт.ст.'
        f'\nВлажность: {response["fact"]["humidity"]}%'
        f'\nСкорость ветра: {response["fact"]["wind_speed"]} м/с'
        f'\nНаправление ветра: {WIND_DIR[response["fact"]["wind_dir"]]}'
    )

    return message


def check_tokens() -> bool:
    """
    Проверяет доступность переменных окружения, которые необходимы программе.
    Если отсутствует хотя бы одна переменная окружения —
    функция должна вернуть False, иначе — True.
    """
    response = True
    if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, YANDEX_API_KEY]):
        response = False
    return response


def send_weather(lat, lon, bot):
    try:
        response = get_api_answer(lat, lon)
        message = parse_weather(response)
    except Exception as error:
        message = f'Сбой в работе программы: {error}'
        logger.error(error)

    send_message(bot, message)


def weather_by_text(update, context):
    coords = update.message.text.replace(',', '.').split()
    if len(coords) < 2:
        send_message(
            context.bot,
            'Должно быть два числа.'
        )
        return
    try:
        lat, lon = float(coords[0]), float(coords[1])
    except ValueError:
        send_message(context.bot, 'Что-то пошло не так.')
        return
    if not -90 <= lat <= 90:
        send_message(
            context.bot,
            'Значение широты между -90 и 90.'
        )
        return

    if not -180 <= lon <= 180:
        send_message(
            context.bot,
            'Значение долготы между -180 и 180.'
        )
        return
    send_weather(lat, lon, context.bot)


def weather_by_location(update, context):
    lat = update.message.location['latitude']
    lon = update.message.location['longitude']
    send_weather(lat, lon, context.bot)


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = [[KeyboardButton('Местоположение', request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=(
            f'Привет, {name}. Передайте ваше местоположение с помощью кнопки'
            '\nили наберите координаты через пробел (широта долгота)'
        ),
        reply_markup=reply_markup
    )


def time_reply(update, context):
    if update.callback_query.data == '2':
        send_message(context.bot, 'Пока не работает.')
    elif update.callback_query.data == '6':
        send_message(context.bot, 'Пока не работает.')


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        error = (
            'Отсутствует одна или более из обязательных переменных окружения:'
            ' PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID.'
            ' Программа принудительно остановлена.'
        )
        logger.critical(error)
        sys.exit(error)

    updater = Updater(token=TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.location, weather_by_location)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, weather_by_text)
    )
    updater.dispatcher.add_handler(CallbackQueryHandler(time_reply))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    handler = StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    main()
