"""Телеграмм бот. Ловец сновидений. Минимальная рабочая версия."""
import logging
import os

import speech_recognition as sr
import telegram
from dotenv import load_dotenv
from pydub import AudioSegment
from serpapi import GoogleSearch
from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater

from exceptions import SendMessageError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GOOGLE_TOKEN = os.getenv('GOOGLE_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    format='%(asctime)s | %(name)s | %(levelname)s | '
           '%(funcName)s | %(message)s',
    level=logging.DEBUG,
)


def send_message(bot, chat_id, message):
    """Отправляет сообщения в чат."""
    try:
        bot.send_message(chat_id, message)
    except telegram.error.TelegramError as e:
        raise SendMessageError(e) from e


def send_photo(bot, chat_id, image, caption):
    """Отправляет сообщения в чат."""
    try:
        bot.send_photo(
            chat_id,
            image,
            caption=f'Текст сна: {caption}',
        )
    except telegram.error.TelegramError as e:
        raise SendMessageError(e) from e


def get_image(query):
    """Получаем изображение из текста сновидения."""
    search = GoogleSearch(
        {
            "q": query,
            "location": "Austin,Texas",
            "ijn": "0",
            "device": "desktop",
            "api_key": GOOGLE_TOKEN
        }
    )
    result = search.get_dict()
    lighthouse_photo = result.get('inline_images')[0].get('thumbnail')
    return lighthouse_photo


def write_text(update: Update, context: CallbackContext):
    """Обработчик введенного в ручную текста."""
    lighthouse = get_image(update.message.text)
    chat = update.effective_chat
    msg = 'Спасибо, я получил описание твоего сна и подобрал маячок,' \
          'он поможет тебе восстановить сновидение!\n'
    try:
        send_message(context.bot, chat.id, msg)
    except SendMessageError:
        logging.error(f'Ошибка отправки сообщения боту: `{msg}`')

    msg = update.message.text
    try:
        send_photo(context.bot, chat.id, lighthouse, caption=msg)
    except SendMessageError:
        logging.error(f'Ошибка отправки сообщения боту: `{msg}`')


def say_voice(update: Update, context: CallbackContext):
    """
    Обработчик голосового ввода, преобразует его текст.
    Ищет маячок сновидения и прикрепляет его к нему. Использует
    `google serpapi` для поиска, и сврис google для перевода голоса.
    """
    chat = update.effective_chat
    file_id = update.message.voice.file_id
    audio_tg = context.bot.get_file(file_id=file_id)

    audio_tg.download('captured.ogg')
    ogg_version = AudioSegment.from_ogg('captured.ogg')
    # play(ogg_version)
    ogg_version.export('output.wav', format="wav")

    r = sr.Recognizer()
    with sr.AudioFile('output.wav') as source:
        audio = r.record(source)

    text_dream = ''
    try:
        text_dream = r.recognize_google(audio, language='ru-RU')
        logging.info(f'Текст файла преобразован {text_dream}')
    except sr.UnknownValueError:
        logging.error(
            "Google Speech Recognition could not understand audio"
        )
    except sr.RequestError as e:
        logging.error(
            "Could not request results from Google Speech Recognition "
            "service; {0}".format(e))

    lighthouse = get_image(text_dream)
    try:
        send_photo(context.bot, chat.id, lighthouse, caption=text_dream)
    except SendMessageError:
        logging.error(f'Ошибка отправки сообщения боту: `{text_dream}`')


def main():  # noqa: C901
    """Основная логика работы бота."""
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, say_voice))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, write_text))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print('\nStarting https://t.me/my_dreamcatcher_bot'
          '\n(Quit the bot with CONTROL-C.)')
    try:
        main()
    except KeyboardInterrupt:
        print('\nShutdown dreamcatcher ...')
        os._exit(0)
