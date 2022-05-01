import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

updater = Updater(token=TELEGRAM_TOKEN)
bot = Bot(token=TELEGRAM_TOKEN)
URL = 'http://rutor.info'


def wake_up(update, context):
    chat = update.effective_chat
    message = 'Я помогу найти торрент с rutor! Напиши мне поисковый запрос'
    context.bot.send_message(chat_id=chat.id, text=message)


def search(update, context):
    chat = update.effective_chat
    text = update['message']['text']
    search_url = f'{URL}/search/{text}'
    request = requests.get(search_url)
    soup = BeautifulSoup(request.text, 'lxml')
    link_list = soup.find('div', id='index').find_all('tr', limit=11)
    for torrent in link_list:
        links = torrent.select('a[href*="/torrent"]')
        name = torrent.text
        downloads = torrent.find('a', class_='downgif')
        for link in links:
            link = link.get('href')
            download = downloads.get('href')
            message = (
                f'Название файла: {name} '
                f'Ссылка на файл: {URL}{link} '
                f'Ссылка на скачку: {download} '
            )
            context.bot.send_message(chat_id=chat.id, text=message)


if __name__ == '__main__':
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, search))
    updater.start_polling()
    updater.idle()
