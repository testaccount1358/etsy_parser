import time
import requests
from selenium import webdriver
import json
from telegram import Bot
import yaml

from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.by import By
categories = [
    'Accessories',
    'Art+and+Collectibles',
    'Baby',
    'Bags+and+Purses',
    'Bath+and+Beauty',
    'Books%2C+Movies+and+Music',
    'Clothing',
    'Craft+Supplies+and+Tools',
    'Electronics+and+Accessories',
    'Gifts',
    'Home+and+Living',
    'Jewelry',
    'Paper+and+Party+Supplies',
    'Pet+Supplies',
    'Shoes',
    'Toys+and+Games',
    'Weddings'
]

def get_etsy_new_items_for_category(category, page_num=1):
    items_on_pages = []
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Firefox(options=options)

    while page_num <= 3:  # Parsing the first 3 pages
        etsy_url = f'https://www.etsy.com/search?q={category}&order=date_desc&page={page_num}'
        driver.get(etsy_url)
        list_items = driver.find_elements(By.XPATH, "//ol/li")

        for item in list_items:
            item_title = item.find_element('h3').text
            item_link = item.find_element('a', class_='listing-link').get_atribute('href')
            items_on_pages.append({'title': item_title, 'link': item_link})

        page_num += 1

    return items_on_pages


def load_data_from_json():
    try:
        with open('etsy_data.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data_to_json(data):
    with open('etsy_data.json', 'w') as file:
        json.dump(data, file, indent=4)

def compare_with_previous_data(current_data, previous_data):
    new_items = [item for item in current_data if item not in previous_data]
    return new_items

def send_to_telegram(message, bot_token, channel_id):
    bot = Bot(token=bot_token)
    bot.send_message(chat_id=channel_id, text=message)


def main():
    while True:
        # Load config from a YAML file
        with open('config.yml', 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)

        bot_token = cfg['telegram_bot_token']
        channel_id = cfg['telegram_channel_id']

        previous_data = load_data_from_json()

        for category in categories:
            current_data = get_etsy_new_items_for_category(category)
            # new_items = compare_with_previous_data(current_data, previous_data)

            # if new_items:
            #     for item in new_items:
            #         send_to_telegram(f"New item in {category}: {item['title']} - {item['link']}", bot_token, channel_id)

            previous_data.extend(current_data)

        save_data_to_json(previous_data)
        
        time.sleep(60)

if __name__ == "__main__":
    main()