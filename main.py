from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackContext, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import os
from dotenv import load_dotenv
import emoji


clock_emoji = emoji.emojize(":alarm_clock:")
year_emoji = emoji.emojize(":anxious_face_with_sweat:")


load_dotenv()
secret_token = os.getenv('TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

updater = Updater(token=secret_token)
dp = updater.dispatcher
jq = updater.job_queue
URL = ''


def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton(f"{clock_emoji} Установить напоминание", callback_data='1'),
            InlineKeyboardButton(f"{year_emoji} Узнать сколько лет", callback_data='2'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['Сколько лет?',
                                   'Поздравления']], resize_keyboard=True)
    context.bot.send_sticker(chat.id,
                             'CAACAgIAAxkBAAEEmoxibpXK7cJMxRUdnqKdGq9AyPpzMQACnxMAAp7OCwABIu98Bcogr3ckBA'
                             )
    context.bot.send_message(
        chat_id=chat.id,
        text='{}, опять забыл(а) поздравить друга?! Ну ничего, теперь мы все исправим'.format(name),
        reply_markup=button
        )
    context.bot.send_message(chat_id=chat_id,
                             text="вот чем я могу помочь",
                             reply_markup=reply_markup
                             )


def button(update, _):
    query = update.callback_query
    variant = query.data
    if variant == '1':
        query.answer()
        query.edit_message_text(text=f"Скоро эта функция будет доделана")
    elif variant == '2':
        query.answer()
        query.edit_message_text(text=f"А эта будет доделана еще быстрее")


def unknown_command(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Извините я не понял команду, выберите команду ниже."
    )


def main():
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
