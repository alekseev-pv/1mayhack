import os
from time import sleep

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater
from telegram.ext import Filters, MessageHandler

load_dotenv()
tg_token = os.getenv('TOKEN')


DATABASE = []


def get_input_and_formation_url(user_input):
    DATABASE.append(user_input)
    number_auto = user_input[0]
    num, region = number_auto[:6], number_auto[6:]
    sts = user_input[1]
    return get_data_from_brouser(f'https://гибдд.рф/check/fines#{num}+{region}+{sts}')


def get_data_from_brouser(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome("chromedriver.exe", options=options)
    browser.get(url)
    sleep(3)
    button = browser.find_element(by=By.XPATH,
                                  value='//*[@id="checkFines"]/p[4]/a')
    button.click()
    sleep(3)
    HTML = browser.page_source
    browser.close()
    soup = BeautifulSoup(HTML, 'html.parser')
    data_inp = soup.find(
        'div', {'id': 'checkFinesSheet'}).find(
        'p', {'class': 'title-doc'}
    ).text
    fine = soup.find("p", {"class": "check-space check-message"}).text
    if fine == ('В результате проверки не были найдены сведения '
                'о неуплаченных штрафах'):
        return f'Ура, штрафов не найдено\n\n{data_inp}'
    return (f'{data_inp}\nОй, кажется есть штрафы, '
            f'лучше проверить на сайте\n\n'
            f'{url}')


def user_input(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text=(f'Оке, приступим {name} введи номер авто и номер СТС с отступом 1 пробел, '
              f'например: а777аа777 99аа999999')
    )


def show_fines(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(chat_id=chat.id, text=f'Минутку {name}, проверяю информацию...')
    user_input = update.message.text.split()
    if len(user_input) == 2:
        result = get_input_and_formation_url(user_input)
        context.bot.send_message(chat_id=chat.id, text=result)


def start(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/yes'], ['/no']], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}. хочешь проверить твои штрафы?',
        reply_markup=button
    )


def say_by(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(chat_id=chat.id, text=f'Оке, успехов {name}')


def main():
    updater = Updater(token=tg_token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('no', say_by))
    updater.dispatcher.add_handler(CommandHandler('yes', user_input))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, show_fines))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
