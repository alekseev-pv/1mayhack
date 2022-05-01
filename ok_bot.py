 # coding: utf-8
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv 
from img_generation import generate_image

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TOKEN')

WAKE_UP_TEXT = (
    'В мире, где роботы уже переводят тексты, доставляют еду'
    ' и пишут картины, людям остается только недоумевать.'
    ' Первыми, кто начал недоумевать, стали пользователи'
    ' социальной сети "Одноклассники". Они недоумевали задолго'
    ' до наступления власти машин 🤖\nЭтот бот мониторит'
    ' официальное сообщество Яндекса в одноклассниках и присылает'
    ' вам комментарии пользователей в его записях.'
)

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s'
    '%(filename)s:%(funcName)s:%(lineno)s - %(message)s'
)
stram_handler = logging.StreamHandler(sys.stdout)
rotating_file_handler = RotatingFileHandler(
    'ok_bot.log', maxBytes=50000000, backupCount=5
)
rotating_file_handler.setFormatter(formatter)

logger.setLevel('DEBUG')
logger.addHandler(stram_handler)
logger.addHandler(rotating_file_handler)


def wake_up(update, context):
    logger.debug('Starting wake_up')
    chat = update.effective_chat

    button = ReplyKeyboardMarkup([['/one_more_comment']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=WAKE_UP_TEXT,
        reply_markup=button,
    )

def new_comment(update, context):
    logger.debug('Starting new_comment')
    generate_image()
    chat = update.effective_chat
    pic=os.path.expanduser("media/ready_img/1.png")

    context.bot.send_photo(chat.id, photo=open(pic, 'rb'))

def check_tokens():
    if not TELEGRAM_TOKEN:
        raise Exception('Не задан токен для ТГ бота в файле .env. Ключ - TELEGRAM_TOKEN')
    if not os.getenv('OK_APP_PUBLIC_KEY'):
        raise Exception(
            'Не задан токен публичный ключ приложения в одноклассниках'
            ' в файле .env. Ключ - OK_APP_PUBLIC_KEY'
        )
    if not os.getenv('OK_SESSION_SECRET_KEY'):
        raise Exception(
            'Не задан Session_secret_key приложения в одноклассниках'
            ' в файле .env. Ключ - OK_SESSION_SECRET_KEY'
        )
    if not os.getenv('OK_ACCESS_TOKEN'):
        raise Exception(
            'Не задан вечный access_token приложения в одноклассниках'
            ' в файле .env. Ключ - OK_ACCESS_TOKEN'
        )

def main():
    logger.debug('Starting main')
    check_tokens()
    updater = Updater(token=TELEGRAM_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('one_more_comment', new_comment))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()