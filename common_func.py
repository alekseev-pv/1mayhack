from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup
from dotenv import load_dotenv
from pprint import pprint
import requests
import logging
import json 
import os


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    )

def get_iam_token():
    # curl -d "{\"yandexPassportOauthToken\":\"<OAuth-token>\"}" "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    headers = {'Content-Type': 'application/json', 'charset': 'UTF-8'} 
    data = json.dumps(
        {"yandexPassportOauthToken": os.getenv('TOKEN_YNX')},
        indent = 4
        )
    iam_token = requests.post(url, data=data, headers=headers)

    return iam_token.json()

def translate(text, lang='ru'):
    body = {
        "targetLanguageCode": lang,
        "texts": text,
        "folderId": os.getenv('FOLDER_ID'),
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_iam_token()['iamToken']}"
    }
    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
        json = body,
        headers = headers
    )

    return response.json().get("translations")[0].get("text")

def get_random_recipe():
    try:
        response = requests.get(
            'https://www.themealdb.com/api/json/v1/1/random.php'
        )
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

def get_recipe_from_ingredient(ingredient):
    try:
        response = requests.get(
            f'www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}'
            )
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

#print(get_iam_token())

#data = get_random_recipe().get('meals')[0].get('strInstructions')
pprint(get_random_recipe()) # .get('hits')[3].get('recipe'))
