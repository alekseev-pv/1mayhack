import logging
import os
from typing import Optional

import requests
from dotenv import load_dotenv
from telegram import (
    ReplyKeyboardMarkup, InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram import Update
from telegram.ext import (
    CommandHandler, Updater, Filters,
    CallbackContext, MessageHandler
)


load_dotenv()

logging.basicConfig(
    filename='basic_log.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv('TOKEN')
# Place your telegram token in '.env'f ile with a variable name 'TOKEN'

API_KEY = os.getenv('API-KEY')
# Reg API-key on 'https://kinopoiskapiunofficial.tech/' and place it in '.env'
# OR replace it with mine, it is for free
# API_KEY = '9b71b2ed-79d2-4f6a-9d72-897193566306'

URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'

updater = Updater(token=TOKEN)

headers = {
    'X-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}


def start(update: Update, context: CallbackContext) -> None:
    """Function that help handle a '/start' command from user."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = ReplyKeyboardMarkup(
        [
            ['/find_film'],
            ['/help']
        ],
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id,
        text=(f'Привет, {name}! Меня зовут Ferdinand Slogan! '
              f'Нажми /help чтобы познакомиться со мной поближе!'),
        reply_markup=buttons
    )


def help_message(update: Update, context: CallbackContext) -> None:
    """Shows help message after request."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=('команда /start запускает бота\n' +
              'команда /find_film запускает поиск информации по фильму\n' +
              'команда /help выводит помощь'
              )
    )


def get_film_by_text_filter(keyword: str) -> str:
    """Gets movie info from api."""
    response = requests.get(URL, headers=headers, params={'keyword': keyword})
    lst_films = response.json().get('items')
    if len(lst_films) == 0:
        return f'Не могу найти фильм {keyword}'
    elif len(lst_films) == 1:
        film = lst_films[0]
        country = film['countries'][0]['country']
        genre = film['genres'][0]['genre']
        name = film['nameRu']
        year = film['year']
        rating_imdb = film['ratingImdb']
        rating_kinopoisk = film['ratingKinopoisk']
        poster = film['posterUrlPreview']
        film_info = [
            f'Название: {name}',
            f'Страна: {country}',
            f'Жанр: {genre}',
            f'Год: {year}',
            f'Рейтинг imdb: {rating_imdb}',
            f'Рейтинг кинопоиска: {rating_kinopoisk}',
            f'{poster}'
        ]
        if name is None:
            f'Не могу найти фильм {keyword}'
        return '\n'.join(film_info)
    else:
        film_id = []
        for film in lst_films:
            film_id.append(str(film['nameRu']) +
                           ': id ' +
                           str(film['kinopoiskId']))
        return (f'Я нашёл много фильмов с упоминанием <i>{keyword}</i>\n' +
                '\n<i><b>Полный список:</b></i>\n' + '\n' +
                '\n'.join(film_id) + '\n\nУточните свой запрос'

                )


def get_kinopoisk_url(keyword: str) -> Optional[str]:
    response = requests.get(URL, headers=headers, params={'keyword': keyword})
    lst_films = response.json().get('items')
    if len(lst_films) == 0 or len(lst_films) > 1:
        return None
    film = lst_films[0]
    kinopoisk_id = film['kinopoiskId']
    url = f'https://www.kinopoisk.ru/movie/{kinopoisk_id}/play/'
    return url


def invite_to_input_film(update: Update, context: CallbackContext) -> None:
    """Returns a little message to welcome to input name of film."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='<b><i>Введите название фильма:</i></b>',
        parse_mode='HTML'
    )


def show_movie_info(update: Update, context: CallbackContext) -> None:
    """Shows user a movie info."""
    chat = update.effective_chat
    last_message = update.message.text
    url = get_kinopoisk_url(last_message)
    button_inline_out = InlineKeyboardButton(
        text='Искать на конопоиске',
        url='https://www.kinopoisk.ru/'
    )
    if url is None:
        context.bot.send_message(
            chat_id=chat.id,
            text=get_film_by_text_filter(last_message),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(
                [[button_inline_out]]
            )
        )
    button_inline = InlineKeyboardButton(
        text='Смотреть на кинопоиске',
        url=url
    )
    context.bot.send_message(
        chat_id=chat.id,
        text=get_film_by_text_filter(last_message),
        reply_markup=InlineKeyboardMarkup(
            [[button_inline]]
        ),
        parse_mode='HTML'
    )


def main():
    """Main function that runs a bot via polling."""
    updater.dispatcher.add_handler(
        CommandHandler('start', start)
    )
    updater.dispatcher.add_handler(
        CommandHandler('help', help_message)
    )
    updater.dispatcher.add_handler(
        CommandHandler('find_film', invite_to_input_film)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, show_movie_info)
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
