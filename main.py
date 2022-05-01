import os
import requests

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from dotenv import load_dotenv

load_dotenv()

ENDPOINT = 'https://api.edamam.com/api/recipes/v2'

APPLICATION_ID = os.getenv('APPLICATION_ID')
APPLICATION_KEY = os.getenv('APPLICATION_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID') #в окружении создать файл .env и добавить туда свой чат id

REQUEST_PARAMS = {
    'type': 'public',
    'q': '',
    'app_id': APPLICATION_ID,
    'app_key': APPLICATION_KEY,
    'mealType': 'Breakfast',
}

updater = Updater(token=TELEGRAM_TOKEN)

NUMB_OF_RECEIPT = 0


def get_api_answer(ingridients):
    """Делает запрос к эндпоинту."""
    REQUEST_PARAMS['q'] = ingridients
    try:
        full_response = requests.get(ENDPOINT, params=REQUEST_PARAMS)
    except Exception:
        pass
    full_response = full_response.json()
    return full_response


def parse_receipt(full_response):
    """Получаем все рецепты."""
    all_receipt = full_response.get('hits')
    return all_receipt


def parse_title(receipt):
    """Получаем название блюда."""
    label = receipt.get('recipe').get('label')
    return label


def parse_link(receipt):
    """Получаем ссылку на блюдо."""
    link = receipt.get('recipe').get('url')
    return link


def cook_it(update, context):
    """Отправляем ссылку на блюдо."""
    chat = update.effective_chat
    global NUMB_OF_RECEIPT
    global ALL_RECEIPT
    receipt = ALL_RECEIPT[NUMB_OF_RECEIPT]
    context.bot.send_message(chat.id, parse_link(receipt))


def next_receipt(update, context):
    """Следующий рецепт."""
    chat = update.effective_chat
    global NUMB_OF_RECEIPT
    global ALL_RECEIPT
    NUMB_OF_RECEIPT = NUMB_OF_RECEIPT+1
    if NUMB_OF_RECEIPT != len(ALL_RECEIPT):
        receipt = ALL_RECEIPT[NUMB_OF_RECEIPT]
        label = parse_title(receipt)
        context.bot.send_message(chat.id, label)
    else:
        context.bot.send_message(chat.id, 'это последний рецепт')


def previous_receipt(update, context):
    """Предыдущий рецепт."""
    chat = update.effective_chat
    global NUMB_OF_RECEIPT
    global ALL_RECEIPT
    NUMB_OF_RECEIPT = NUMB_OF_RECEIPT-1
    if NUMB_OF_RECEIPT == 0:
        receipt = ALL_RECEIPT[NUMB_OF_RECEIPT]
        label = parse_title(receipt)
        context.bot.send_message(chat.id, label)
    else:
        context.bot.send_message(chat.id, 'это первый рецепт')


def take_receipt(update, context):
    """Основная функция."""
    chat = update.effective_chat
    ingridients = update.message.text.lower().rstrip()
    full_response = get_api_answer(ingridients)
    global ALL_RECEIPT
    ALL_RECEIPT = parse_receipt(full_response)
    if ALL_RECEIPT == []:
        context.bot.send_message(
            chat_id=chat.id,
            text='Попробуйте ввести другие продукты'
        )
    receipt = ALL_RECEIPT[NUMB_OF_RECEIPT]

    label = parse_title(receipt)
    context.bot.send_message(
        chat_id=chat.id,
        text=label
    )

    buttons = ReplyKeyboardMarkup([
        ['/previous', '/next'],
        ['/cook_it']
    ], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text="Выбери действие",
        reply_markup=buttons
    )


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Введи ингриденты на английском/ и получишь рецепт на завтрак'.format(name),
    )


if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('cook_it', cook_it))
    updater.dispatcher.add_handler(CommandHandler('next', next_receipt))
    updater.dispatcher.add_handler(CommandHandler(
        'previous',
        previous_receipt
    ))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, take_receipt))

    updater.start_polling()

    updater.idle()
