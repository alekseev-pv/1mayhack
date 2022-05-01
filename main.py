import os
import re
import requests
import telegram
from telegram.ext import Updater, MessageHandler, Filters
from dotenv import load_dotenv


load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

BOT = telegram.Bot(token=TG_TOKEN)
UPDATER = Updater(token=TG_TOKEN)

ENDPOINT = 'https://od-api.oxforddictionaries.com/api/v2'
HEADERS={'app_id': APP_ID,
         'app_key': APP_KEY,
         }

EN = r'[a-z]+'
RU = r'[а-я]+'


def get_word(update):
    """Получает слово из сообщения."""
    word = update.message.text
    return word.lower()


def get_word_language(word):
    """Определяет язык слова."""
    if re.match(RU, word):
        return 'ru'
    return 'en'


def get_translations(word_id, language):
    """Получает список переводов."""
    source_lang_translate = language
    if language == 'ru':
        target_lang_translate = 'en'
    else:
        target_lang_translate = 'ru'

    url = (f'{ENDPOINT}/translations/{source_lang_translate}/{target_lang_translate}/{word_id}')

    request = requests.get(url=url, headers=HEADERS)

    translations = request.json().get('results')[0].get('lexicalEntries')[0].get('entries')[0].get('senses')[0].get('translations')
    return translations


def translate(update, context):
    """Запускает остальные функции и отправляет сообщение с переводом или переводами в чат."""
    chat = update.effective_chat

    word = get_word(update)
    lang = get_word_language(word)
    translations = get_translations(word_id=word, language=lang)

    for translation in translations:
        translation = translation.get('text')
        context.bot.send_message(chat_id=chat.id, text=translation)


def main():
    UPDATER.dispatcher.add_handler(MessageHandler(Filters.text, translate))

    UPDATER.start_polling(poll_interval=0.5)
    UPDATER.idle


if __name__ == '__main__':
    main()
