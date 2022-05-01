from math import acos, asin, atan, cos, sin, tan, pi
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FORMULAS = {
    'osnov_formulas': 'pichers/osnformuls.jpg',
    'summ_formulas': 'pichers/sumugol.jpg',
    'cast_formulas': 'pichers/prividenia.jpg',
    'teorema_cos': 'pichers/teoremacosinusof.jpg',
    'teorema_sin': 'pichers/teoremasinusov.jpg',
    'for_sum_in_proiz': 'pichers/transformersummmuliti.jpg',
    'for_proiz_in_sum': 'pichers/transformmultisumm.jpg',
    'polovinogo_ugla': 'pichers/polovinsformul.jpg',
    '2xugol': 'pichers/2xugol.jpg',
    '3xugol': 'pichers/3xugol.jpg',
    '4x5xugol': 'pichers/4x5xugol.jpg',
}

def get_4x5xugol(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['4x5xugol'], 'rb'))


def get_3xugol(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['3xugol'], 'rb'))


def get_2xugol(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['2xugol'], 'rb'))


def get_polovinogo_ugla(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['polovinogo_ugla'], 'rb'))



def get_proiz_in_sum(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['for_proiz_in_sum'], 'rb'))


def get_sum_in_proiz(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['for_sum_in_proiz'], 'rb'))


def get_teorema_sin(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['teorema_sin'], 'rb'))


def get_teorema_cos(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['teorema_cos'], 'rb'))


def get_cast_formulas(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['cast_formulas'], 'rb'))

def get_osn_formulas(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['osnov_formulas'], 'rb'))

def get_summ_formulas(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, open(FORMULAS['summ_formulas'], 'rb'))



def count_angles(stroka):
    """функция считает значение угла"""
    angles_var = None
    trg_func = ''
    var_trg_func = ''
    for i in stroka:
        if not i.isdigit():
            trg_func += i
        elif i.isdigit():
            var_trg_func += i
    trg_func_list = [cos, sin, tan]
    arc_func_list = [acos, asin, atan]
    var_trg_func = int(var_trg_func)
    for i in range(len(trg_func_list)):
        if trg_func_list[i].__name__ == trg_func:
            var_trg_func *=  pi / 180
            angles_var = trg_func_list[i](var_trg_func)
            return str(angles_var)
        elif arc_func_list[i].__name__ == trg_func:
            angles_var = arc_func_list[i](var_trg_func)
            angles_var *= 180 / pi
            return f'{angles_var} градусов'
        elif trg_func == 'ctg':
            var_trg_func *=  pi / 180
            angles_var = 1 / tan(var_trg_func)
            return str(angles_var)


def start(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = ReplyKeyboardMarkup([
                ['/osn_formulas', '/summ_formulas', '/cast_formulas'],
                ['/teorema_cos', '/teorema_sin'],
                ['/for_sum_in_proiz', '/for_proiz_in_sum'],
                ['/polovinogo_ugla', '/2xugol', '/3xugol', '/4x5xugol']
            ], resize_keyboard=True)
    text = (f'Привет {name}.'
        '\nЯ умею вычислять тригонометрические функции.'
        '\nНапиши в чате тригонометрическую функцию по примеру,'
        '\nsin60\ncos60\ntan60\nctg60\nacos1\nasin1\natan1\n'
        'Значение углов указывать в градусах без пробела.')
    context.bot.send_message(chat_id=chat.id, text=text, reply_markup=buttons)


def message_angles(update, context):
    chat = update.effective_chat
    messege = update.message.text
    text = f'{messege} = {count_angles(messege)}'
    context.bot.send_message(chat_id=chat.id, text=text)
    
def main():
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('osn_formulas', get_osn_formulas))
    updater.dispatcher.add_handler(CommandHandler('summ_formulas', get_summ_formulas))
    updater.dispatcher.add_handler(CommandHandler('cast_formulas', get_cast_formulas))
    updater.dispatcher.add_handler(CommandHandler('teorema_cos', get_teorema_cos))
    updater.dispatcher.add_handler(CommandHandler('teorema_sin', get_teorema_sin))
    updater.dispatcher.add_handler(CommandHandler('for_sum_in_proiz', get_sum_in_proiz))
    updater.dispatcher.add_handler(CommandHandler('for_proiz_in_sum', get_proiz_in_sum))
    updater.dispatcher.add_handler(CommandHandler('polovinogo_ugla', get_polovinogo_ugla))
    updater.dispatcher.add_handler(CommandHandler('2xugol', get_2xugol))
    updater.dispatcher.add_handler(CommandHandler('3xugol', get_3xugol))
    updater.dispatcher.add_handler(CommandHandler('4x5xugol', get_4x5xugol))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, message_angles))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()