import os
import requests

from telegram.ext import (CommandHandler,
                          Updater,
                          ConversationHandler,
                          MessageHandler,
                          Filters)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from dotenv import load_dotenv

load_dotenv()

token = os.getenv('TOKEN')

url = "https://fitness-calculator.p.rapidapi.com/bmi"
url2 = "https://fitness-calculator.p.rapidapi.com/dailycalorie"

headers = {
    "X-RapidAPI-Host": "fitness-calculator.p.rapidapi.com",
    "X-RapidAPI-Key": "8660cff8famshaa55d0275edf774p1ea9dbjsn77a81d6f7eab"
}

GET_AGE, GET_WEIGHT, GET_HEIGHT, GET_BMI = range(4)
(GET_AGE2, GET_WEIGHT2,
 GET_HEIGHT2, GET_GENDER,
 GET_DCR, GET_LEVEL) = range(6)


def bmi(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([['/cancel']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Введите свой возраст',
        reply_markup=button
    )
    return GET_AGE


def get_age(update, _):
    global AGE
    try:
        AGE = int(update.message.text)
        if AGE < 15 or AGE > 80:
            update.message.reply_text('Неверное значение')
            return GET_AGE
        else:
            update.message.reply_text(
                'Введите свой вес в кг')
            return GET_WEIGHT
    except ValueError:
        update.message.reply_text('Неверное значение')
        return GET_AGE


def get_weight(update, _):
    global WEIGHT
    try:
        WEIGHT = int(update.message.text)
        if WEIGHT < 40 or WEIGHT > 160:
            update.message.reply_text('Неверное значение')
            return GET_WEIGHT
        else:
            update.message.reply_text(
                'Введите свой рост в см')
            return GET_HEIGHT
    except ValueError:
        update.message.reply_text('Неверное значение')
        return GET_WEIGHT


def get_height(update, _):
    global HEIGHT
    try:
        HEIGHT = int(update.message.text)
        if HEIGHT < 130 or HEIGHT > 230:
            update.message.reply_text('Неверное значение')
            return GET_HEIGHT
        else:
            reply_keyboard = [['Рассчитать ИМТ']]
            markup_key = ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True)
            update.message.reply_text(
                'нажми "Рассчитать ИМТ"',
                reply_markup=markup_key,)
            return GET_BMI
    except ValueError:
        update.message.reply_text('Неверное значение')
        return GET_HEIGHT


def get_bmi(update, _):
    querystring = {"age": f"{AGE}", "weight": f"{WEIGHT}",
                   "height": f"{HEIGHT}"}
    print(querystring)
    response = requests.request("GET", url,
                                headers=headers, params=querystring)
    response = response.json()
    bmi = response.get('data').get('bmi')
    range = response.get('data').get('healthy_bmi_range')
    update.message.reply_text(
        f'Ваш индекс массы тела: {bmi}, Границы нормы: {range}',
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def dcr(update, context):
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([['/cancel']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Введите свой возраст',
        reply_markup=button
    )
    return GET_AGE2


def get_age2(update, _):
    global AGE
    try:
        AGE = int(update.message.text)
        if AGE < 15 or AGE > 80:
            update.message.reply_text('Неверное значение')
            return GET_AGE2
        else:
            update.message.reply_text(
                'Введите свой вес в кг')
            return GET_WEIGHT2
    except ValueError:
        update.message.reply_text('Неверное значение')
        return GET_AGE2


def get_weight2(update, _):
    global WEIGHT
    try:
        WEIGHT = int(update.message.text)
        if WEIGHT < 40 or WEIGHT > 160:
            update.message.reply_text('Неверное значение')
            return GET_WEIGHT2
        else:
            update.message.reply_text(
                'Введите свой рост в см')
            return GET_HEIGHT2
    except ValueError:
        update.message.reply_text('Неверное значение')
        return GET_WEIGHT2


def get_height2(update, _):
    global HEIGHT
    try:
        HEIGHT = int(update.message.text)
        if HEIGHT < 130 or HEIGHT > 230:
            update.message.reply_text('Неверное значение')
            return GET_HEIGHT2
        else:
            reply_keyboard = [['male', 'female']]
            markup_key = ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True)
            update.message.reply_text('Выбирете пол', reply_markup=markup_key)
            return GET_GENDER
    except ValueError:
        update.message.reply_text('Неверное значение')
        return GET_HEIGHT2


def get_gender(update, _):
    global GENDER
    GENDER = update.message.text
    reply_keyboard = [['без упражнений', '1-3 раза в неделю'],
                      ['4-5 раз в неделю', 'ежедневно']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        'Выбирете уровень активности',
        reply_markup=markup_key,)
    return GET_LEVEL


def get_level(update, _):
    global LEVEL
    level_dict = {
        'без упражнений': 'level_1',
        '1-3 раза в неделю': 'level_2',
        '4-5 раз в неделю': 'level_3',
        'ежедневно': 'level_4',
    }
    LEVEL = level_dict[update.message.text]
    reply_keyboard = [['Рассчитать дневную норму калорий']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        'нажми "Рассчитать дневную норму калорий"',
        reply_markup=markup_key,)
    return GET_DCR


def get_dcr(update, _):
    querystring = {"age": f"{AGE}", "gender": f"{GENDER}",
                   "height": f"{HEIGHT}", "weight": f"{WEIGHT}",
                   "activitylevel": f"{LEVEL}"}
    print(querystring)
    response = requests.request(
        "GET", url2, headers=headers, params=querystring)
    response = response.json()
    maintain_weight = response.get('data').get('goals').get('maintain weight')
    loss_weight = response.get('data').get('goals').get('Weight loss').get('calory')
    weight_gain = response.get('data').get('goals').get('Weight gain').get('calory')
    update.message.reply_text(
        f'Ваша норма калорий: {maintain_weight}.'
        f' Для потери веса: {loss_weight}.'
        f'Для набора веса: {weight_gain}.',
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel(update, _):
    update.message.reply_text(
        'Сессия остановлена'
        '   /start для начала',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    buttons = ReplyKeyboardMarkup([['/BMI', '/daily_calory_requirement']])
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}. Выбирете параметр для расчета.'.format(name),
        reply_markup=buttons
    )


def main():
    updater = Updater(token)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('BMI', bmi)],
        states={
            GET_AGE: [MessageHandler(Filters.text & ~Filters.command,
                      get_age)],
            GET_WEIGHT: [MessageHandler(Filters.text & ~Filters.command,
                         get_weight)],
            GET_HEIGHT: [MessageHandler(Filters.text & ~Filters.command,
                         get_height)],
            GET_BMI: [MessageHandler(Filters.text & ~Filters.command,
                      get_bmi)],
        },
        fallbacks=[CommandHandler('cancel', cancel)])
    )
    updater.dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('daily_calory_requirement', dcr)],
        states={
            GET_AGE2: [MessageHandler(Filters.text & ~Filters.command,
                       get_age2)],
            GET_WEIGHT2: [MessageHandler(Filters.text & ~Filters.command,
                          get_weight2)],
            GET_HEIGHT2: [MessageHandler(Filters.text & ~Filters.command,
                          get_height2)],
            GET_GENDER: [MessageHandler(Filters.regex('^(male|female)$'),
                         get_gender)],
            GET_LEVEL: [MessageHandler(Filters.regex(
                '^(без упражнений|1-3 раза в неделю|4-5 раз в неделю|ежедневно)$'),
                get_level)],
            GET_DCR: [MessageHandler(Filters.text & ~Filters.command,
                      get_dcr)],
        },
        fallbacks=[CommandHandler('cancel', cancel)])
    )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
