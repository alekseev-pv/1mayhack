from telegram import Bot, GameHighScore

from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup

import os

from dotenv import load_dotenv 

from determinant_game import DeterminantGame

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def wake_up(update, context):
    # В ответ на команду /start 
    # будет отправлено сообщение 'Спасибо, что включили меня'
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = ReplyKeyboardMarkup(game.keyboard_mainmenu, resize_keyboard=True)

    text = (f'Привет, {name}. Хочешь сыграть со мной в игру?\n'
            'Будь осторожен, а то голова взорвется...\n'
            'Прежде, ознакомся с правилами /rules')

    context.bot.send_message(
        chat_id=chat.id,
        text=text,
        reply_markup=buttons
    )

def dialog(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    text='Хочешь начать заново? /newgame'
    buttons = game.KEYBOARD_MAINMENU
    
    reply = update.message.text
    
    if reply == '1':
        buttons = [['1']]
        text ='1'

    elif reply in game.ARROWS.keys():
        result = game.gaming(reply)
        buttons = result['keyboard']
        text = result['text']

    elif reply in game.NUMBERS.keys():
        result = game.gaming(reply)
        buttons = result['keyboard']
        text = result['text']

    elif reply in ['Начать игру', '/newgame']:
        game.reset()
        buttons = game.keyboard_arrows
        text ='Выбери ячейку для заполнения'

    elif reply in ['Правила', '/rules']:
        buttons = game.KEYBOARD_MAINMENU
        text = game.RULES_INFO

    elif reply == 'О игре':
        buttons = game.KEYBOARD_MAINMENU
        text = game.ABOUT_GAME


    context.bot.send_message(
        chat_id=chat.id,
        text=text,
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

def main():
    
    updater = Updater(token=TELEGRAM_TOKEN)

    # Регистрируется обработчик CommandHandler;
    # он будет отфильтровывать только сообщения с содержимым '/start'
    # и передавать их в функцию wake_up()
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))

    # Регистрируется обработчик MessageHandler;
    # из всех полученных сообщений он будет выбирать только текстовые сообщения
    # и передавать их в функцию say_hi()
    updater.dispatcher.add_handler(MessageHandler(Filters.text, dialog))

    # Метод start_polling() запускает процесс polling, 
    # приложение начнёт отправлять регулярные запросы для получения обновлений.
    updater.start_polling()
    # Бот будет работать до тех пор, пока не нажмете Ctrl-C
    updater.idle()


if __name__ == '__main__':
    game=DeterminantGame()
    main()