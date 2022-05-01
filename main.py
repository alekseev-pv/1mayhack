from cgitb import text
import requests, os
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()
auth_token = os.getenv('TOKEN')

deck = requests.get('https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1').json()
deck_id = deck['deck_id']

DICT ={
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

total = 0
total_aces = 0
player_wins = 0
bot_wins = 0
bot_total = 0
bot_first_card_value = 0

def draw_a_card():
    """Берем карту из колоды."""
    response = requests.get(f'https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count=1').json()
    return response['cards'][0]

def check_result():
    global total, player_wins, bot_wins



def bot_plays(update, context):
    global bot_total, total, player_wins, bot_wins
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text=f'Твои очки: {total}. Моя очередь!')

def wellcome(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/draw', '/rules']], resize_keyboard=True)
    card = draw_a_card()
    card_pic = card['image']
    context.bot.send_message(chat_id=chat.id, 
                             text='Добрый день, {}! Сыграем в Блэкджек?'.format(name),
                             reply_markup=button)
    context.bot.send_message(chat_id=chat.id, text=f'Как дилер я беру первую карту!')
    context.bot.send_photo(chat.id, card_pic)
    if card['value'] == 'ACE':
        bot_first_card_value = 11
    else:
        bot_first_card_value = DICT[card['value']]
    context.bot.send_message(chat_id=chat.id, text=f'И так, у меня {bot_first_card_value}. Твой черед!') 




def lets_play(update, context):
    global total, total_aces, player_wins, bot_wins
    chat = update.effective_chat
    card = draw_a_card()
    card_pic = card['image']
    context.bot.send_photo(chat.id, card_pic)
    #Так как туз может принимать два значения, для него создана отдельная обработка
    if not card['value'] == 'ACE':
        total += DICT[card['value']]
    else:
        if (total + 11) > 21:
            total += 1
        else:
            total += 11
            total_aces += 1
    #Если перебор, проверяем остались ли у игрока тузы, значение которых можно уменьшить
    while total_aces > 0 and total > 21:
        total -= 10
        total_aces -= 1
    if total > 21:
        bot_wins += 1
        context.bot.send_message(chat_id=chat.id, text=f'Общее число очков: {total}')
        context.bot.send_message(chat_id=chat.id, text=f'Вы проиграли! Повезет в другой раз, возможно.')
        context.bot.send_message(chat_id=chat.id, text=f'Вы - {player_wins}. Бот - {bot_wins}.')
        total = 0
    elif total == 21:
        player_wins += 1
        context.bot.send_message(chat_id=chat.id, text=f'Общее число очков: {total}')
        context.bot.send_message(chat_id=chat.id, text=f'Поздравляю! Победа Ваша!')
        context.bot.send_message(chat_id=chat.id, text=f'Вы - {player_wins}. Бот - {bot_wins}.')
        total = 0
    else:
        button = ReplyKeyboardMarkup([['/draw', '/stop']], resize_keyboard=True)
        context.bot.send_message(chat_id=chat.id, 
                                 text=f'Общее число очков: {total}',
                                 reply_markup=button)



def main():
    updater = Updater(token=auth_token)
  

    updater.dispatcher.add_handler(CommandHandler('draw', lets_play))
    updater.dispatcher.add_handler(CommandHandler('start', wellcome))
    updater.dispatcher.add_handler(CommandHandler('stop', bot_plays))
    #updater.dispatcher.add_handler(MessageHandler(Filters.text, choose_your_destiny))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main() 
