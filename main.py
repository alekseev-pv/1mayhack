import os
import pprint as p
import re

import requests
import telegram
from dotenv import load_dotenv
from telegram.ext import Filters, MessageHandler, Updater

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


def get_translations(word_id, source_lang_translate):
    """Получает список переводов."""
    if source_lang_translate == 'ru':
        target_lang_translate = 'en'
    else:
        target_lang_translate = 'ru'

    url = (f'{ENDPOINT}/translations/{source_lang_translate}/{target_lang_translate}/{word_id}')

    request = requests.get(url=url, headers=HEADERS)

    translations = request.json().get('results')[0].get('lexicalEntries')[0].get('entries')[0].get('senses')[0].get('translations')
    return translations


def get_translation_message(translations):
    message = 'Переводы:\n\n'

    if len(translations) == 1:
        message = 'Перевод:\n\n'
        for translation in translations:
            translation = translation.get('text')
            message += f'1) {translation};\n'
        return message

    i = 1
    for translation in translations:
        translation = translation.get('text')
        message += f'{i}) {translation};\n'
        i += 1
    return message


def get_info(update, context):
    """Запускает остальные функции и отправляет сообщение с переводом или переводами в чат."""
    chat = update.effective_chat

    word = get_word(update)
    lang = get_word_language(word)
    translations = get_translations(word_id=word, source_lang_translate=lang)
    info = get_word_info(word, lang)
    definitions = get_word_definitions(info)

    translation_message = get_translation_message(translations)
    definition_message = get_definition_message(definitions)
    audio = get_pronunciations(info)

    context.bot.send_message(chat_id=chat.id, text=translation_message)
    context.bot.send_message(chat_id=chat.id, text=definition_message)
    context.bot.send_audio(chat_id=chat.id, audio=audio)


def get_word_info(word_id, source_lang):
    if source_lang == 'en':
        url = f'{ENDPOINT}/entries/{source_lang}/{word_id}'
        request = requests.get(url=url, headers=HEADERS)
        info = request.json().get('results')[0].get('lexicalEntries')[0].get('entries')[0]
    return(info)


def get_pronunciations(info):
    pronunciations = info.get('pronunciations')[0].get('audioFile')
    return pronunciations


def get_word_definitions(info):
    subsenses = info.get('senses')[0].get('subsenses')
    definitions = []
    for subsense in subsenses:
        definitions += subsense.get('definitions')
    return definitions


def get_definition_message(definitions):
    message = 'Определения:\n\n'
    if len(definitions) == 1:
        message = 'Определения:\n\n'
        for definition in definitions:
            message += f'1) {definition};\n'
        return message

    i = 1
    for definition in definitions:
        message += f'{i}) {definition};\n'
        i += 1
    return message


def main():
    UPDATER.dispatcher.add_handler(MessageHandler(Filters.text, get_info))

    UPDATER.start_polling(poll_interval=0.5)
    UPDATER.idle


if __name__ == '__main__':
    main()
