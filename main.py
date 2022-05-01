from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import artic as art
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
cur_page = []

def art_template(*args):
     return 'Название - {}\nАвтор - {}\nМесто создания - {}\nОригинальный размер - {}\nИзображение - {}'.format(*args)

def start(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/random_art', '/start_search']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Я Бот-гид по Чикагскому институту искусств.\nЧто будем делать?'.format(name),
        reply_markup=button
    )


def get_random(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([['/random_art', '/start_search']], resize_keyboard=True)
    data = art.random_art()
    context.bot.send_message(
         chat_id=chat.id,
         reply_markup=button,
         text=art_template(
              data.get('title'),
              data.get('artist_display').replace("\n",","),
              data.get('place_of_origin'),
              data.get('dimensions'),
              art.get_image_link(data.get('image_id'))
          )
    )

def start_search(update, context):
     chat = update.effective_chat
     context.bot.send_message(
          chat_id=chat.id,
          text='Для поиска введите текст на английском языке (иначе результат поиска будет пуст!).',
          reply_markup=ReplyKeyboardRemove(),
     )

def search_result(update, context):
     chat = update.effective_chat
     button = ReplyKeyboardMarkup([['/next_page', '/show_page']], resize_keyboard=True)
     search_criteria = update['message']['text']
     data = art.search_art(search_criteria)
     pagination = data.get('pagination')
     total_res = pagination.get('total')
     total_pages = pagination.get('total_pages')
     current_page = pagination.get('current_page')
     cur_page.append(data.get('data'))
     context.bot.send_message(
          chat_id=chat.id,
          text='Всего найдено - {}\nВсего страниц - {}\nТекущая страница - {}'.format(total_res, total_pages, current_page),
          reply_markup=button,
     )


def show_page(update, context):
     chat = update.effective_chat
     for record in cur_page[0]:
          context.bot.send_message(
          chat_id=chat.id,
          text=art_template(
               record.get('title'),
               record.get('artist_display').replace("\n",","),
               record.get('place_of_origin'),
               record.get('dimensions'),
               art.get_image_link(record.get('image_id'))
          )
    )



def next_page():
     ...


def pre_page():
     ...


def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('random_art', get_random))
    updater.dispatcher.add_handler(CommandHandler('start_search', start_search))
    updater.dispatcher.add_handler(CommandHandler('next_page', next_page))
    updater.dispatcher.add_handler(CommandHandler('show_page', show_page))    
    updater.dispatcher.add_handler(MessageHandler(Filters.text, search_result))    


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
     main()
