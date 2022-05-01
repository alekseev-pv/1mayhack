from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup
from common_func import * 
from dotenv import load_dotenv
import requests
import logging
import os


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

def new_recipe(update, context):
    chat = update.effective_chat
    recipe, picture = get_random_recipe()
    context.bot.send_message(chat.id, recipe)
    context.bot.send_photo(chat.id, picture)

def say_hi(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Привет, я помогу выбрать блюдо!')

def wake_up(update, context):
    chat = update.effective_chat
    name = update.effective_user.first_name
    # buttons = ReplyKeyboardMarkup([
    #             ['Который час?', 'Определи мой ip'],
    #             ['/random_digit']
    #         ])

    button = ReplyKeyboardMarkup([['/newrecipe']], resize_keyboard=True)

    context.bot.send_message(chat_id=chat.id, 
                             text=f'Привет, {name}. Посмотри, какой рецепт я тебе нашёл!',
                             reply_markup=button
                             )
    context.bot.send_message(chat.id, get_random_recipe())

def main():
    updater = Updater(token=os.getenv('TOKEN_TELEGA'))
   
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('newrecipe', new_recipe))
    # updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))
    updater.start_polling(poll_interval=20.0)
    updater.idle()


if __name__ == '__main__':
    main()
