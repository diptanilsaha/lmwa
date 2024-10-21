import requests
from typing import List
from config import Config

def strip_dict_keys(d: dict) -> dict:
    keys = d.keys()
    new_dict = {}
    for k in keys:
        new_dict[k.strip()] = d[k]

    return new_dict

def get_books_from_api(title: str, count: int):
    page_count = (count // 20) + 1
    books = []
    for i in range(1, page_count + 1):
        data = [
            ('page', str(i)),
            ('title', title)
        ]
        r = requests.get(Config.API_URL, params=data)
        api_data = r.json()['message']
        for book_data in api_data:
            books.append(strip_dict_keys(book_data))

    return books[:count]