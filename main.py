import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater
import os
import random

updater = Updater(token='5302339331:AAFZAJ8bthskbRohjsgpvjltyfbRSUmxyp4')
URL = 'https://yesno.wtf/api'
URL2 = 'http://rzhunemogu.ru/RandJSON.aspx?CType=1'
DIR = 'audio/'
DIR_MESSAGE = 'mental_info/'
DIR_IMAGE = 'result/'


def get_new_image():
    response_2 = requests.get(URL).json(strict=False)
    random_gif = response_2.get('image')
    return random_gif


def get_new_story():
    response_2 = requests.get(URL2).json(strict=False)
    response_story = response_2.get('content')
    return response_story


def new_joke(update, context):
    chat = update.effective_chat
    context.bot.send_video(chat.id, get_new_image())
    context.bot.send_message(chat.id, get_new_story())
    context.bot.send_audio(
        chat.id, audio=open(
            os.path.join(DIR, random.choice(os.listdir(DIR))), 'rb'
        )
    )


def get_verdict(update, context):
    chat = update.effective_chat
    message = open(
            os.path.join(
                DIR_MESSAGE, random.choice(os.listdir(DIR_MESSAGE))
                ), encoding="utf-8"
        )
    image = open(
        os.path.join(DIR_IMAGE, random.choice(os.listdir(DIR_IMAGE))), 'rb'
    )
    message = message.read()
    context.bot.send_message(chat.id, f'Поздравляю, у тебя {message}')
    context.bot.send_photo(chat.id, image)


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['😂', '😊', '😐', '🙁', '🤮', '/new', '/verdict']], resize_keyboard=True
    )

    context.bot.send_message(
        chat_id=chat.id,
        text='Привет 👋, {}. Посмотри, какие картинки и анекдоты я тебе нашёл.Я хочу увидеть твои реакции и проанализировать, вперед я расскажу о тебе много нового'.format(name),
        reply_markup=button
    )

    context.bot.send_video(chat.id, get_new_image())
    context.bot.send_message(chat.id, get_new_story())
    context.bot.send_audio(chat.id, audio=open('audio/test.mp3', 'rb'))


updater.dispatcher.add_handler(CommandHandler('start', wake_up))
updater.dispatcher.add_handler(CommandHandler('new', new_joke))
updater.dispatcher.add_handler(CommandHandler('verdict', get_verdict))

updater.start_polling()
updater.idle()
