from playwright.sync_api import sync_playwright
import time
import re
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import re

class ArenaStore:
    def __init__(self):
        pass

    def extract_sku(self, title_text: str) -> str:
        if not title_text:
            return 'None'
        # https://arenastore.com.ua/cholovichi_krosivki_saucony_triumph_23_s21023-155
        # S21023-155
        url = title_text.strip().lower()
        url = re.sub(r'\.html\b|\/$', '', url)
        url_parts = url.split('_')
        if len(url_parts) > 1:
            potential_sku = url_parts[-1].upper()
            if any(char.isdigit() for char in potential_sku):
                return potential_sku
        return 'None'
    
    def view_resource(self):
        product_selector = ".product-layout.product-grid"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless = False)
            page = browser.new_page()
            page.goto("https://arenastore.com.ua/obuv/krossovki-i-kedy/size/11/10-5/krosivki-i-kedi111/kros-vki-sportivn114/style/run/pol/choloviche/")
            page.wait_for_selector(product_selector)
            #page.wait_for_load_state("domcontentloaded")
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
        soup = BeautifulSoup(content, 'html.parser')
        products = soup.find_all('div', class_='product-thumb-hover')
        list_result = []
        for item in products:
            item_tag = item.find('div', class_='product-inner')
            try:
                name_tag = item_tag.find('h2', class_='product-name').find('a')
                if name_tag:
                    name = name_tag.text.strip()
                    href = name_tag.get('href', '')
                    sku = self.extract_sku(href)
                else:
                    name = "Unkown Model"
                    href = ""
                    sku = "None"
                both_prices_tag = item_tag.find('p', class_='price')
                span_new = both_prices_tag.find('span', class_='price-new')
                current_price_raw = 0
                old_price_raw = 0
                if span_new:
                    span_old = both_prices_tag.find('span', class_='price-old')
                    current_price_raw = span_new.get_text()
                    old_price_raw = span_old.get_text() if span_old else current_price_raw
                else:
                    current_price_raw = both_prices_tag.get_text()
                    old_price_raw = current_price_raw
                list_item = {
                    'Model': name,
                    'Href': href,
                    'Sku': sku,
                    'Raw_Price': int(re.sub(r"\D", "", current_price_raw)),
                    'Raw_Old_Price': int(re.sub(r"\D", "", old_price_raw))
                }
                list_result.append(list_item)
            except Exception as error:
                print({ error })
                continue
        return list_result