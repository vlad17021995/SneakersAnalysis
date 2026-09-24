from playwright.sync_api import sync_playwright
import time
import re
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd

class NewBalance:
    def __init__(self):
        pass
    
    def view_resource(self):
        target_url = "https://newbalance.ua/store/man/vzutta/dla-bigu?&size[0]=34&size[1]=33"
        product_selector = ".products__item"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless = False)
            page = browser.new_page()
            page.goto(target_url)
            page.wait_for_selector(product_selector)
            while True:
                current_products = page.locator(product_selector)
                initial_count = current_products.count()
                last_product = current_products.last
                last_product.scroll_into_view_if_needed()
                new_items_loaded = False
                for _ in range(6):
                    time.sleep(0.5)
                    if page.locator(product_selector).count() > initial_count:
                        new_items_loaded = True
                        break
                if not new_items_loaded:
                    break
            html_content = page.content()
            browser.close()
            return self.fill_out_list(html_content)

    def fill_out_list(self, content):
        print('fill called')
        soup = BeautifulSoup(content, 'html.parser')
        products = soup.find_all('li', class_='products__item')
        list_result = []
        for item in products:
            try:
                brand = item.get('data-brand')
                name = item.get('data-name')
                Sku = item.get('data-product-id')
                prices = item.find('div', class_='prices')
                all_prices = prices.find_all('span', class_='prices__price')
                current_price_raw = 0
                old_price_raw = 0
                if len(all_prices) == 1:
                    current_price_raw = prices.find('span', class_='prices__price').text.strip() 
                    old_price_raw = prices.find('span', class_='prices__price').text.strip() 
                else:
                    current_price_raw = prices.find('span', class_='prices__price_discount').text.strip()
                    old_price_raw = prices.find('span', class_='prices__price_old').text.strip()
                list_item = {
                    'Model': brand + ' ' + name,
                    'Sku': Sku,
                    'Raw_Price': int(re.sub(r"\D", "", current_price_raw)),
                    'Raw_Old_Price': int(re.sub(r"\D", "", old_price_raw)) 
                }
                list_result.append(list_item)
            except Exception as error:
                print(error)
                continue
        return list_result             