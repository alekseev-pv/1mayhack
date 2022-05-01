import logging
import os
import random
import sqlite3 as sq
import sys
from logging import StreamHandler

import cv2
import requests
import telebot
from dotenv import load_dotenv
from PIL import Image
from telebot import types

import generate_img
import settings

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    handlers=[StreamHandler(stream=sys.stdout)]
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать, {0.first_name}!\nЯ — <b>{1.first_name}</b>, "
        "бот созданный в развлекательных целях, который не несет "
        "смысловой нагрузки.".format(message.from_user, bot.get_me()),
        parse_mode = "html")
    menu(message)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == ("Меню" or "меню" or "Menu" or "menu"):
        menu(message)


def menu(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton("Получить рандомный пароль", callback_data="item1")
    item2 = types.InlineKeyboardButton("Получить цвет RGB", callback_data="item2")
    item3 = types.InlineKeyboardButton("Изменить картинку", callback_data="item3")
    item5 = types.InlineKeyboardButton("загадать слово", callback_data="item5")
    markup.add(item1, item2, item3, item5)
    bot.send_message(message.chat.id, "Что будем делать?", reply_markup = markup)


def menu_edit_photo(message):
    markup1 = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Повернуть на лево", callback_data="btn1")
    btn2 = types.InlineKeyboardButton("Перевернуть на 180", callback_data="btn2")
    btn3 = types.InlineKeyboardButton("Повернуть на право", callback_data="btn3")
    btn4 = types.InlineKeyboardButton("Пиксель арт", callback_data="btn4")
    btn5 = types.InlineKeyboardButton("Сделать черно-белым", callback_data="btn5")
    markup1.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, "Что будем делать?", reply_markup = markup1)


@bot.callback_query_handler(func=lambda c:c.data)
def answer_callback(callback):
    variable = "Отправьте картинку или url-ссылку"
    if callback.data == "item1":
        sent = bot.reply_to(callback.message, "Введите длинну пароля (не больше 100).")
        bot.register_next_step_handler(sent, generate_password)
    if callback.data == "item2":
        sent = bot.reply_to(
            callback.message,
            "Введите цвет в формате RGB через запятую от 0 до 255, например так "
            "(255, 255, 255) или название цвета на английском."
        )
        bot.register_next_step_handler(sent, create_photo)
    if callback.data == "item3":
        menu_edit_photo(callback.message)
    if callback.data == "item4":
        menu(callback.message)
    if callback.data == "item5":
        sent = bot.reply_to(
            callback.message,
            "Гадание по какой хрене навязаной разработчиком, "
            "введите слово и если оно есть, придет предсказание)."
        )
        bot.register_next_step_handler(sent, book)

    if callback.data == "btn1":
        sent = bot.reply_to(callback.message, variable)
        bot.register_next_step_handler(sent, get_to_turn_90)
    if callback.data == "btn2":
        sent = bot.reply_to(callback.message, variable)
        bot.register_next_step_handler(sent, get_to_turn_180)
    if callback.data == "btn3":
        sent = bot.reply_to(callback.message, variable)
        bot.register_next_step_handler(sent, get_to_turn_270)
    if callback.data == "btn4":
        sent = bot.reply_to(callback.message, variable)
        bot.register_next_step_handler(sent, get_photo_pixelate)
    if callback.data == "btn5":
        sent = bot.reply_to(callback.message, variable)
        bot.register_next_step_handler(sent, get_photo_bw)


def generate_password(message):
    message_to_save = message.text
    if message_to_save.isdigit():
        if int(message_to_save) > 99:
            sent = bot.reply_to(message, "Введите длинну пароля (не больше 100).")
            bot.register_next_step_handler(sent, generate_password)
        else:
            result = []
            for _ in range(3):
                item = ""
                count = 0
                for _ in range(int(message_to_save)):
                    if count == 4:
                        item += "-"
                        count = 0
                    else:
                        value = random.choice(settings.VARIABLES)
                        item += random.choice(value)
                        count += 1
                result.append(item)
                count = 0
            for i in range(len(result)):
                bot.send_message(message.chat.id, result[i])

            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Да", callback_data="item1")
            item4 = types.InlineKeyboardButton("Нет", callback_data="item4")
            markup.add(item1, item4)
            bot.send_message(message.chat.id, "Продолжим?", reply_markup = markup)
    else:
        sent = bot.reply_to(message, "Укажите длиннулину пароля в цифрах.")
        bot.register_next_step_handler(sent, generate_password)


def menu_choice(message, item):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item2 = types.InlineKeyboardButton("Да", callback_data=item)
    item4 = types.InlineKeyboardButton("Нет", callback_data="item4")
    markup.add(item2, item4)
    bot.send_message(message.chat.id, "Продолжим?", reply_markup = markup)


def create_photo(message):
    message_to_save = message.text
    text_rgb = "Введите три цифры через запятую или название цвета на английском."
    if "," in message_to_save:
        if len(message_to_save.split(",")) == 3:
            R, G, B = message_to_save.split(",")
            R, G, B = R.strip(), G.strip(), B.strip()
            if R.isdigit() and G.isdigit() and B.isdigit():
                R, G, B = int(R), int(G), int(B)
                if R > 255 or G > 255 or B > 255:
                    bot.send_message(message.chat.id, "В RGB не может быть значений больше 255.")
                    menu_choice(message, "item2")
                else:
                    message_to_save = R, G, B
                    try:
                        new_img = Image.new('RGB', (500, 500), message_to_save)
                        bot.send_photo(message.chat.id, new_img)
                        menu_choice(message, "item2")
                    except ValueError:
                        bot.send_message(
                            message.chat.id,
                            "Введите цвет в формате RGB через запятую или название цвета на английском."
                        )
                        menu_choice(message, "item2")
            else:
                bot.send_message(message.chat.id, text_rgb)
                menu_choice(message, "item2")
        else:
            bot.send_message(message.chat.id, text_rgb)
            menu_choice(message, "item2")
    else:
        bot.send_message(message.chat.id, text_rgb)
        menu_choice(message, "item2")


def menu_photo(message, name, item):
    if os.path.isfile(f"{name}.jpg"):
        os.remove(f"{name}.jpg")
    markup = types.InlineKeyboardMarkup(row_width=2)
    item2 = types.InlineKeyboardButton("Да", callback_data=item)
    item4 = types.InlineKeyboardButton("Нет", callback_data="item4")
    markup.add(item2, item4)
    bot.send_message(message.chat.id, "Продолжим?", reply_markup = markup)


def get_photo(message):
    name = message.from_user.username
    if message.content_type == "photo":
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f"{name}.jpg", "wb") as new_file:
            new_file.write(downloaded_file)
        return (f"{name}.jpg", name)
    else:
        url = message.text
        try:
            raw = requests.get(url, stream=True).raw
            return (raw, name)
        except Exception as e:
            logging.error(f"Ошибка ответа API: {e}")
            return False


def get_photo_bw(message):
    im = get_photo(message)
    if not im:
        bot.send_message(message.chat.id, f"Ошибка ответа API")
        menu_photo(message, message.from_user.first_name, "btn5")

    img_grey = cv2.imread(im[0], cv2.IMREAD_GRAYSCALE)
    img_binary = cv2.threshold(img_grey, 128, 255, cv2.THRESH_BINARY)[1]
    cv2.imwrite(im[0], img_binary)

    bot.send_photo(message.chat.id, Image.open(im[0]))
    menu_photo(message, im[1], "btn5")


def get_photo_pixelate(message):
    im = get_photo(message)
    if not im:
        bot.send_message(message.chat.id, f"Ошибка ответа API")
        menu_photo(message, message.from_user.first_name, "btn4")
    image_pixelate = generate_img.pixelate(Image.open(im[0]))
    bot.send_photo(message.chat.id, image_pixelate)
    menu_photo(message, im[1], "btn4")


def get_to_turn_90(message):
    im = get_photo(message)
    if not im:
        bot.send_message(message.chat.id, f"Ошибка ответа API")
        menu_photo(message, message.from_user.first_name, "btn3")
    bot.send_photo(message.chat.id, Image.open(im[0]).transpose(Image.ROTATE_90))
    menu_photo(message, im[1], "btn3")


def get_to_turn_180(message):
    im = get_photo(message)
    if not im:
        bot.send_message(message.chat.id, f"Ошибка ответа API")
        menu_photo(message, message.from_user.first_name, "btn2")
    bot.send_photo(message.chat.id, Image.open(im[0]).transpose(Image.ROTATE_180))
    menu_photo(message, im[1], "btn2")


def get_to_turn_270(message):
    im = get_photo(message)
    if not im:
        bot.send_message(message.chat.id, f"Ошибка ответа API")
        menu_photo(message, message.from_user.first_name, "btn1")
    bot.send_photo(message.chat.id, Image.open(im[0]).transpose(Image.ROTATE_270))
    menu_photo(message, im[1], "btn1")


def book(message):
    message_to_save = message.text
    with sq.connect("book.db") as con:
        cur = con.cursor()

        cur.execute("""SELECT line 
                       FROM book JOIN words_book USING(book_id)
                       WHERE word = ?""", (message_to_save,))

        data = cur.fetchall()
        if data:
            result = random.choices(data)
            bot.send_message(message.chat.id, result)
            menu_choice(message, "item5")
        else:
            bot.send_message(
                message.chat.id,
                "Такого слова у нас нет, попробуй другое"
            )
            menu_choice(message, "item5")

if __name__ == '__main__':
     bot.infinity_polling()