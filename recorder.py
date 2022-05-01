import os
import speech_recognition as sr
import telebot
from telebot import types
from dotenv import load_dotenv

recorder = sr.Recognizer()

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_STASHED')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID_STASHED'))

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,
        ('/help - этот список.\n'
         '/rec - запись с микрофона и после вывод текста в сообщении.'
         )
    )


@bot.message_handler(commands=['rec'])
def rec(message):
    markup = types.InlineKeyboardMarkup()
    buttonA = types.InlineKeyboardButton('ЗАПИСЬ', callback_data='recording')
    markup.row(buttonA)
    bot.send_message(
        message.chat.id,
        'Для начала записи нажмите ЗАПИСЬ',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == "recording":
            chat_id = call.message.chat.id
            text = record(chat_id)
            msg = f'Чат: {chat_id} Записанное сообщение: {text}'
            bot.send_message(chat_id, msg)


def record(chat_id):
    """Записывает звук и переводит в русский текст."""
    text = 'Ничего не записали.'
    try:
        with sr.Microphone() as source:
            recorder.adjust_for_ambient_noise(source)
            bot.send_message(
                chat_id,
                'Начинаем запись. Длительность записи 8 секунд.'
            )
            data = recorder.record(source, duration=8)
            bot.send_message(chat_id, 'Запись успешно записана.')
            text = recorder.recognize_google(data, language='ru')
    except sr.UnknownValueError:
        bot.send_message(chat_id, 'Ничего не слышно.')
        text = 'пусто'
    except Exception as ex:
        print(f'Some error {type(ex)} {ex}')
    finally:
        return text


def main():
    bot.infinity_polling()


if __name__ == '__main__':
    main()
