from playwright.sync_api import sync_playwright
import time
import re
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd

class Puma:
    def __init__(self):
        pass
    
    def view_resource(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless = False)
            page = browser.new_page()
            page.goto("https://ua.puma.com/uk/sportivnye-tovary-dlja-muzhchin/obuv/krossovki-dlja-bega.html?size=44.5,45")
            page.wait_for_load_state("domcontentloaded")
            PRODUCT_SELECTOR = "div.grid__item.image-sv01" 
            SPINNER_SELECTOR = "div.spinner, div.loader, .loading-spinner"
            try:
                button = page.locator("a:has-text('Показати все')").first
                if button.is_visible():
                    button.click()
                    page.wait_for_timeout(2000)
            except Exception:
                print("⚠️ Кнопку 'Показати все' не знайдено, можливо сайт одразу ввімкнув скрол.")
            last_count = 0
            no_change_turns = 0
            max_no_change_turns = 10 # Спроб скролу без нових товарів до фіналу
            while True:
                current_products = page.locator(PRODUCT_SELECTOR)
                current_count = current_products.count()
                if current_count > 0:
                    last_product = current_products.last
                    last_product.scroll_into_view_if_needed()
                else:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                page.wait_for_timeout(800)
                spinner = page.locator(SPINNER_SELECTOR).first
                while spinner.is_visible():
                    page.wait_for_timeout(500)
                if current_count == last_count:
                    no_change_turns += 1
                    if no_change_turns >= max_no_change_turns:
                        break
                else:
                    last_count = current_count
                    no_change_turns = 0
                page.wait_for_timeout(400)
            html_content = page.content()
            browser.close()
        return self.fill_out_list(html_content)
    
    def fill_out_list(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        #product-item
        products = soup.find_all('div', class_='product-item')
        #products = soup.find_all('div', class_='product-item__info')
        list_result = []
        for item in products:
            try:
                Sku = item.get('data-product-sku')
                item_tag = item.find('div', class_='product-item__info')
                name_tag = item_tag.find('a', class_='product-item__name')
                name = name_tag.text.strip() if name_tag else "Unkown Puma Model"
                both_prices_tag = item_tag.find('div', class_='product-item__price')
                price_tag = both_prices_tag.find('span', class_='special-price').find('span', 'price-wrapper')
                price_text = price_tag.get('data-price-amount') if price_tag else '0'
                old_price_tag = both_prices_tag.find('span', class_='old-price').find('span', 'price-wrapper')
                old_price_text = old_price_tag.get('data-price-amount') if old_price_tag else '0'
                list_item = {
                    'Model': name,
                    'Sku': Sku,
                    'Raw_Price': price_text,
                    'Raw_Old_Price': old_price_text
                }
                list_result.append(list_item)
            except Exception:
                continue
        return list_result

