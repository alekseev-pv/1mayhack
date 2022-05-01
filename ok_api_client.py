 # coding: utf-8
import json, requests, hashlib
from typing import List
import os

from dotenv import load_dotenv 
load_dotenv()

YANDEX_GROUP_ID = 48235937660955
NUMBER_OF_COMMENTS = 200
TOPIC_ID = 70586809524251

# Во многом использую решение https://github.com/OlegShir/Ok_api_publish_post/blob/main/ok.py
class OK_api:

    def __init__(self) -> None:
        self.gid = YANDEX_GROUP_ID
        self.api_server = 'https://api.ok.ru/fb.do'
        self.SSK = os.getenv('OK_SESSION_SECRET_KEY')
        self.app_public_key = os.getenv('OK_APP_PUBLIC_KEY')
        self.access_token = os.getenv('OK_ACCESS_TOKEN')

    def get_topics(self) -> list:
        """Получить список id постов сообщества.
        У одноклассников нет API метода для получения списка
        обсуждений группы, поэтому вытаскиваем их из html"""
        topics_file = open("ok_yandex_group_topics.txt", "r")
        topics = []
        for line in topics_file:
            topics.append(int(line))
        topics_file.close()
        return topics

    def get_comments(self, topic_id: int):
        """Вытащить все комментарии из поста."""
        payload = {
            'application_key': self.app_public_key,
            'method': 'discussions.getDiscussionComments',
            'access_token': self.access_token,
            'count': NUMBER_OF_COMMENTS,
            'entityId': topic_id,
            'entityType': 'GROUP_TOPIC',
            'format': 'json',
        }

        payload = self.add_mb5_sig(payload)
        comments_response = requests.get(self.api_server, params=payload)
        respon_from_server_json = comments_response.json()
        comments_list = []
        comments_data = respon_from_server_json.get('commentss')
        for comment_item in comments_data:
            comments_list.append(comment_item['text'])
        return comments_list

    def add_mb5_sig(self, dictionary: dict) -> dict:
            """Метод производит расчет подписи запроса API OK в соостветствии с https://apiok.ru/dev/methods/
            и добавляет подпись в запрос"""
            #копируем словарь для возможности его безопасного изменения 
            signature_data = dictionary.copy()
            #убираем из списка параметров session_key/access_token при наличии
            [signature_data.pop(key, '') for key in ['session_key', 'access_token']]
            #параметры сортируются лексикографически по ключам
            lexicograph = sorted(signature_data.items())
            #создаем хранилище
            string_payload = ''
            #параметры соединяются в формате ключ=значение
            for pair in lexicograph:
                string_payload = f'{string_payload}{pair[0]}={pair[1]}'

            #sig = MD5(значения_параметров + session_secret_key);           
            sig = hashlib.md5(f'{string_payload}{self.SSK}'.encode()).hexdigest()
            #добавляем подпись в запрос
            dictionary['sig'] = sig

            return dictionary

if __name__ == '__main__':
    pass
