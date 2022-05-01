import requests as req
from random import randrange

def get_image_link(image_id):
     return f'https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg'

def random_art():
     url = 'https://api.artic.edu/api/v1/artworks/'
     params = {
          'limit': 0,
     }
     response = req.get(url=url, params=params).json()
     total_pages = response.get('pagination').get('total')
     page = randrange(total_pages)
     params = {
          'limit': 1,
          'page': page,
          'fields': 'id,title,image_id,alt_text,artist_display,place_of_origin,dimensions'
     }
     random_data = req.get(url=url, params=params).json()
     return random_data.get('data')[0]
     

def search_art(criteria, page=1):
     url = 'https://api.artic.edu/api/v1/artworks/search'
     params = {
          'q': criteria,
          'page': page,
          'fields': 'id,title,image_id,alt_text,artist_display,place_of_origin,dimensions',
     }
     response = req.get(url=url, params=params)
     return response.json()


def main():
     print(search_art('Russia'))

if __name__ == '__main__':
   main()
