from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from pprint import pprint
import requests
import logging
import os


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    )

app_id = os.getenv('APPID_EDAMAM')
tok = os.getenv('TOKEN_EDAMAM')

URL2 = f'https://api.edamam.com/api/recipes/v2?type=public&q=beef%2Cgarlic%2Cpotato&app_id=90dc949b&app_key=8c02c7426db1f97b64cb5f8a86c23c0f&ingr=3-4&imageSize=REGULAR&field=image'
URL3 = 'https://api.edamam.com/api/recipes/v2?type=public&q=beef%2Cgarlic%2Cpotato&app_id=90dc949b&app_key=8c02c7426db1f97b64cb5f8a86c23c0f&ingr=3-4&imageSize=REGULAR&field=label'
URL = 'https://www.themealdb.com/api/json/v1/1/random.php'

def get_iam_token():
    # curl -d "{\"yandexPassportOauthToken\":\"<OAuth-token>\"}" "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    pass

def translate(text, lang='ru'):
    body = {
        "targetLanguageCode": lang,
        "texts": text,
        "folderId": os.getenv('FOLDER_ID'),
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(os.getenv('IAM_TOKEN'))
    }

    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
        json = body,
        headers = headers
    )

    return response.json().get("translations")[0].get("text")

def get_random_recipe():
    try:
        response = requests.get(URL)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)
    
    #response = response.json().get('meals')[0].get('strInstructions') 
    #random_cat = response[0].get('url')
    title = translate(response.json().get('meals')[0].get('strMeal'))
    picture = response.json().get('meals')[0].get('strMealThumb') 
    man = translate(response.json().get('meals')[0].get('strInstructions'))

    recipe = f'{title}\n{man}'

    return recipe, picture




#data = get_random_recipe().get('meals')[0].get('strInstructions')
pprint(get_random_recipe()) # .get('hits')[3].get('recipe'))
