from bs4 import BeautifulSoup
import requests


def get_news_scraper():
    response = requests.get("https://newslab.ru/afisha/")
    soup = BeautifulSoup(response.text, 'lxml')
    items = soup.find_all('div', class_='af-box-item af-box-item_col4 af-box-item_without-image')
    scraper_content = {}

    for item in items:
        title = item.find('span', class_="af-box-item__title")
        title_text = title.get_text()
        link = item.find('a', class_="af-box-item__link")
        full_link = 'https://newslab.ru' + link['href']
        scraper_content[title_text] = full_link

    return scraper_content
