from dotenv import load_dotenv
import os
import requests
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

ENDPOINT = 'https://api.dictionaryapi.dev/api/v2/entries/en/'

NO_DEFINITION_MESSAGE = "Sorry, no definitions found!"


def start_message(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Enter one english word')


def get_api_definition(word):
    URL = ENDPOINT + word
    response = requests.get(URL)
    response = response.json()
    if isinstance(response, list):
        return response[0].get('meanings')[0].get('definitions')[0].get(
            'definition'
        )
    return NO_DEFINITION_MESSAGE


def get_api_audio(word):
    URL = ENDPOINT + word
    response = requests.get(URL)
    response = response.json()
    phonetics = response[0].get('phonetics')
    for i in range(len(phonetics)):
        answer = phonetics[i].get('audio')
        if answer != "":
            return answer
    return "Sorry, there is no available audio file"


def word_definition(update, context):
    chat = update.effective_chat
    text = get_api_definition(update.message.text)
    context.bot.send_message(
        chat_id=chat.id,
        text="DEFINITION: " + text,
    )
    if text != NO_DEFINITION_MESSAGE:
        audio = get_api_audio(update.message.text)
        context.bot.send_message(
            chat_id=chat.id,
            text=audio,
        )


def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start_message))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text, word_definition)
    )
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
