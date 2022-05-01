import logging
from logging.handlers import RotatingFileHandler
import sys
import random
import re

from PIL import Image, ImageDraw, ImageFont

from ok_api_client import OK_api
from comment_filter import filter_comments

FONT = ImageFont.truetype("Arial.ttf", 15, encoding='UTF-8')
SYMBOLS_ON_ONE_LINE = 62

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s'
    '%(filename)s:%(funcName)s:%(lineno)s - %(message)s'
)
stram_handler = logging.StreamHandler(sys.stdout)
rotating_file_handler = RotatingFileHandler(
    'ok_bot.log', maxBytes=50000000, backupCount=5
)
rotating_file_handler.setFormatter(formatter)

logger.setLevel('DEBUG')
logger.addHandler(stram_handler)
logger.addHandler(rotating_file_handler)

def get_lined_text(text: str):
    """
    Добавить в длинный комментарий символы переноса строки.
    А также подсчитать, сколько строк вышло.
    """
    logger.debug('Starting get_lined_text')
    text_len = len(text)
    pattern = re.compile('(.{0,60}\s)')
    end_index = 0
    lines = 1
    r = pattern.search(text)
    if not r:
        logger.error('Не удалось найти пробел для переноса строки')
    while r and end_index < (text_len - SYMBOLS_ON_ONE_LINE):
        lines += 1
        end_index = r.end()
        text = text[:end_index-1] + '\n' + text[end_index:]
        r = pattern.search(text,end_index + 2)
    return text, lines

def generate_white_background(number_of_lines=1) -> Image:
    """
    Сгенерировать белый фон, на котором будет размещен
    текст комментария.
    """
    logger.debug('Starting generate_white_background')
    # 506 и 60 - ширина и высота белого квадрата
    hight = 30 + (20 * number_of_lines)
    white_background = Image.new('RGB', (506,hight), color=('#FFFFFF'))
    return white_background

def generate_final_img(comment_img: Image) -> Image:
    """
    Склеить изображение с комментарием на белом фоне
    и фоновую картинку.
    """
    logger.debug('Starting generate_final_img')
    background = Image.open('media/backgrounds/robot.jpeg')
    background.thumbnail(([924, 450]), Image.Resampling.LANCZOS)
    background.paste(comment_img, [340, 200])
    return background

def generate_image() -> None:
    """
    Генерация изображения.
    Основная логика генерации:
    - случайным образом выбирается id поста из файла;
    - по API забираются все комментарии из этого поста;
    - комментарии фильтруются по ключевым словам;
    - создается картинка комментария на белом фоне;
    - создается изображение для отправки в ТГ
    """
    logger.debug('Starting generate_image')
    
    api_client = OK_api()
    topics_ids = api_client.get_topics()
    max_len = len(topics_ids) - 1
    while True:
        topic_id = topics_ids[random.randint(0, max_len)]
        comments_raw = api_client.get_comments(topic_id)
        filtered_comments = filter_comments(comments_raw)
        if len(filtered_comments) > 0:
            comments_max_index = len(filtered_comments) - 1
            comment_text = filtered_comments[random.randint(0, comments_max_index)]
            logger.debug(f'Подобрали комментарий: {comment_text}')
            number_of_lines = 1
            if len(comment_text) > SYMBOLS_ON_ONE_LINE:
                logger.debug('Комментарий слишком длинный для одной строки')
                comment_text, number_of_lines = get_lined_text(comment_text)
            break
        logger.info(
            'Не нашлось подходящих комментариев в посте'
            f' {topic_id}. Пробуем выбрать другой.'
        )

    comment_img = generate_white_background(number_of_lines)
    
    draw_text = ImageDraw.Draw(comment_img)
    draw_text.text((10,20), comment_text, font=FONT, fill=('#000'))
    comment_img.save('media/comments_img/1.png')

    background = generate_final_img(comment_img)
    background.save('media/ready_img/1.png')

if __name__ == '__main__':    
    pass