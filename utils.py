import requests
import time
import random

def get_one_page(url):
    response = requests.get(url)
    while response.status_code == 403:
        time.sleep(500 + random.uniform(0, 500))
        response = requests.get(url)
        print(response.status_code)
    if response.status_code == 200:
        print("Successfully access " + url + "!")
        return response.text
    return None