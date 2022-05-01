import os
from time import sleep

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv

import scraper

load_dotenv()

secret_token = os.getenv('TOKEN')


def get_news():
    news_data = scraper.get_news_scraper()
    return news_data


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['/getnews']], 
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id, 
        text='Привет, {}. Я помогу тебе узнать какие события сейчас проходят в Красноярске'.format(name),
        reply_markup=button
    )


def send_news(update, context):
    news_data = get_news()

    chat = update.effective_chat
    for news, link in news_data.items():
        context.bot.send_message(chat_id=chat.id, text=f'{news} {link}')
        sleep(15)


def main():
    updater = Updater(token=secret_token)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('getnews', send_news))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main() 
