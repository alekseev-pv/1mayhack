import codecs
import json
import requests
import os
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()
auth_token = os.getenv('TOKEN')

deck = requests.get(
    'https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1').json()
deck_id = deck['deck_id']

DICT = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'JACK': 10,
    'QUEEN': 10,
    'KING': 10,
}

user_dict = {}


def save_progress(user_dict):
    """Сохраняем прогресс в файл"""
    with open('user_dict.json', 'w', encoding='utf-8') as file:
        json.dump(user_dict, file)


def read_user_dict(user_dict, chat_id, key):
    """Берем локальную переменную из словаря."""
    value = user_dict[chat_id][key]
    return value


def write_user_dict(user_dict, chat_id, key, value):
    """Записываем локальную переменную в словарь."""
    user_dict[chat_id][key] = value


def check_or_create_user(user_dict, chat_id):
    """Проверяем существует ли пользователь
    и в случае отсутствия создаем нового."""
    if chat_id not in user_dict:
        user_dict[chat_id] = {
            'total': 0,
            'total_aces':  0,
            'bot_total_aces': 0,
            'player_wins': 0,
            'bot_wins': 0,
            'bot_total': 0,
            'bot_first_card_value': 0,
        }


def draw_a_card():
    """Берем карту из колоды."""
    response = requests.get(
        f'https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count=1').json()
    return response['cards'][0]


def bot_plays(update, context):
    """Ход бота, а также подсчет результатов"""
    global bot_total, bot_first_card_value
    chat = update.effective_chat

    total = read_user_dict(user_dict=user_dict, chat_id=chat.id, key='total')
    bot_wins = read_user_dict(user_dict=user_dict, chat_id=chat.id, key='bot_wins')
    player_wins = read_user_dict(user_dict=user_dict, chat_id=chat.id, key='player_wins')
    bot_first_card_value = read_user_dict(user_dict=user_dict, chat_id=chat.id, key='bot_first_card_value')
    bot_total = 0
    bot_total_aces = 0

    check_win = False
    button = ReplyKeyboardMarkup([['/start', '/rules']], resize_keyboard=True)
    context.bot.send_message(chat_id=chat.id,
                             text=f'Твои очки: {total}. Моя очередь!')
    context.bot.send_message(chat_id=chat.id,
                             text=f'Напомню, у меня {bot_first_card_value}!')
    bot_total = bot_first_card_value
    while bot_total < 17:
        card = draw_a_card()
        card_pic = card['image']
        context.bot.send_photo(chat.id, card_pic)
        if not card['value'] == 'ACE':
            bot_total += DICT[card['value']]
        else:
            if (bot_total + 11) > 21:
                bot_total += 1
            else:
                bot_total += 11
                bot_total_aces += 1
        while bot_total_aces > 0 and bot_total > 21:
            bot_total -= 10
            bot_total_aces -= 1
        if bot_total > 21:
            player_wins += 1
            context.bot.send_message(chat_id=chat.id,
                                     text=f'У меня {bot_total} очков.')
            context.bot.send_message(chat_id=chat.id,
                                     text='У меня перебор. Тебе повезло.')
            context.bot.send_message(chat_id=chat.id,
                                     text=f'Вы - {player_wins}. Бот - {bot_wins}.',
                                     reply_markup=button)
            check_win = True
        elif bot_total == 21:
            player_wins += 1
            context.bot.send_message(chat_id=chat.id,
                                     text=f'У меня {bot_total} очков.')
            context.bot.send_message(chat_id=chat.id,
                                     text='Чистая победа!')
            context.bot.send_message(chat_id=chat.id,
                                     text=f'Вы - {player_wins}. Бот - {bot_wins}.',
                                     reply_markup=button)
            check_win = True
        elif bot_total >= 17 and bot_total < 21:
            context.bot.send_message(chat_id=chat.id,
                                     text=f'У меня {bot_total}, останавливаюсь.')
        else:
            context.bot.send_message(chat_id=chat.id,
                                     text=f'У меня {bot_total}, продолжаем!')
    if not check_win:
        context.bot.send_message(chat_id=chat.id,
                                 text=f'Итоговый счет: {total} у тебя, {bot_total} у меня.')
        if bot_total <= total:
            player_wins += 1
            context.bot.send_message(chat_id=chat.id,
                                     text='Поздравляю, победа за тобой!')
            context.bot.send_message(chat_id=chat.id,
                                     text=f'Вы - {player_wins}. Бот - {bot_wins}.',
                                     reply_markup=button)
        else:
            bot_wins += 1
            context.bot.send_message(chat_id=chat.id,
                                     text='И... я победил!')
            context.bot.send_message(chat_id=chat.id,
                                     text=f'Вы - {player_wins}. Бот - {bot_wins}.',
                                     reply_markup=button)
    write_user_dict(user_dict=user_dict,
                    chat_id=chat.id,
                    key='bot_wins',
                    value=bot_wins)
    write_user_dict(user_dict=user_dict,
                    chat_id=chat.id,
                    key='player_wins',
                    value=player_wins)
    save_progress(user_dict=user_dict)


def wellcome(update, context):
    """Запуск игры, взятие первой карты ботом."""
    global user_dict
    chat = update.effective_chat
    check_or_create_user(user_dict=user_dict, chat_id=chat.id)
    write_user_dict(user_dict, chat.id, 'total', 0)
    write_user_dict(user_dict, chat.id, 'total_aces', 0)
    write_user_dict(user_dict, chat.id, 'bot_total', 0)
    bot_total_aces = 0
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/draw', '/rules']], resize_keyboard=True)
    card = draw_a_card()
    card_pic = card['image']
    context.bot.send_message(chat_id=chat.id,
                             text='{}, время играть в Блэкджек!'.format(name),
                             reply_markup=button)
    context.bot.send_message(chat_id=chat.id,
                             text='Как дилер я беру первую карту!')
    context.bot.send_photo(chat.id, card_pic)
    if card['value'] == 'ACE':
        bot_first_card_value = 11
        bot_total_aces += 1
    else:
        bot_first_card_value = DICT[card['value']]
    context.bot.send_message(chat_id=chat.id,
                             text=f'И так, у меня {bot_first_card_value}. Твой черед!')
    write_user_dict(user_dict=user_dict,
                    chat_id=chat.id,
                    key='bot_first_card_value',
                    value=bot_first_card_value)
    write_user_dict(user_dict=user_dict,
                    chat_id=chat.id,
                    key='bot_total_aces',
                    value=bot_total_aces)
    save_progress(user_dict=user_dict)


def lets_play(update, context):
    """Взятие карты игроком."""
    chat = update.effective_chat
    button = ReplyKeyboardMarkup([['/start', '/rules']], resize_keyboard=True)
    total = read_user_dict(user_dict=user_dict, chat_id=chat.id, key='total')
    total_aces = read_user_dict(user_dict=user_dict, chat_id=chat.id, key='total_aces')
    bot_wins = read_user_dict(user_dict=user_dict, chat_id=chat.id, key='bot_wins')
    player_wins = read_user_dict(user_dict=user_dict, chat_id=chat.id, key='player_wins')
    card = draw_a_card()
    card_pic = card['image']
    context.bot.send_photo(chat.id, card_pic)
    # Так как туз может принимать два значения, для него создана отдельная обработка
    if not card['value'] == 'ACE':
        total += DICT[card['value']]
    else:
        if (total + 11) > 21:
            total += 1
        else:
            total += 11
            total_aces += 1
    # Если перебор, проверяем остались ли у игрока тузы, значение которых можно уменьшить
    while total_aces > 0 and total > 21:
        total -= 10
        total_aces -= 1
    if total > 21:
        bot_wins += 1
        context.bot.send_message(chat_id=chat.id,
                                 text=f'Общее число очков: {total}')
        context.bot.send_message(chat_id=chat.id,
                                 text='Вы проиграли! Повезет в другой раз, возможно.')
        context.bot.send_message(chat_id=chat.id,
                                 text=f'Вы - {player_wins}. Бот - {bot_wins}.',
                                 reply_markup=button)
        total = 0
    elif total == 21:
        player_wins += 1
        context.bot.send_message(chat_id=chat.id,
                                 text=f'Общее число очков: {total}')
        context.bot.send_message(chat_id=chat.id,
                                 text='Поздравляю! Победа Ваша!')
        context.bot.send_message(chat_id=chat.id,
                                 text=f'Вы - {player_wins}. Бот - {bot_wins}.',
                                 reply_markup=button)
        total = 0
    else:
        button = ReplyKeyboardMarkup([['/draw', '/stop']], resize_keyboard=True)
        context.bot.send_message(chat_id=chat.id,
                                 text=f'Общее число очков: {total}',
                                 reply_markup=button)

    write_user_dict(user_dict=user_dict,
                    chat_id=chat.id,
                    key='total',
                    value=total)
    write_user_dict(user_dict=user_dict,
                    chat_id=chat.id,
                    key='total_aces',
                    value=total_aces)
    write_user_dict(user_dict=user_dict,
                    chat_id=chat.id,
                    key='bot_wins',
                    value=bot_wins)
    write_user_dict(user_dict=user_dict,
                    chat_id=chat.id,
                    key='player_wins',
                    value=player_wins)
    save_progress(user_dict=user_dict)


def talk(update, context):
    """Реакция на разговоры."""
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text='Нет времени на разговоры! Хватай карты!')


def rules(update, context):
    """Показываем правила."""
    chat = update.effective_chat
    text = codecs.open("rules.txt", "r", "utf_8_sig")
    text = text.readlines()
    button = ReplyKeyboardMarkup([['/start', '/rules']], resize_keyboard=True)
    for str in text:
        context.bot.send_message(chat_id=chat.id, text=str, reply_markup=button)


def main():
    global user_dict
    try:
        with open('user_dict.json') as file:
            user_dict = json.load(file)
    except Exception:
        print('Невозможно загрузить словарь.')
    updater = Updater(token=auth_token)

    updater.dispatcher.add_handler(CommandHandler('draw', lets_play))
    updater.dispatcher.add_handler(CommandHandler('start', wellcome))
    updater.dispatcher.add_handler(CommandHandler('stop', bot_plays))
    updater.dispatcher.add_handler(CommandHandler('rules', rules))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, talk))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()