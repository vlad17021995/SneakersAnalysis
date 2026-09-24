from playwright.sync_api import sync_playwright
import time
import re
import numpy as np
from bs4 import BeautifulSoup
import re

class Adidas:
    def __init__(self):
        pass
    def extract_sku(self, title_text: str) -> str:
        if not title_text:
            return 'None'
        regexp = r'\b([a-z]{1,2}[0-9]{4,5})\b'
        title = '-'.join(title_text.split()).lower()
        match = re.search(regexp, title)
        if match:
            return match.group(1)
        return 'None'
    
    def scrab_page(self, content, list):
        soup = BeautifulSoup(content, 'html.parser')
        products = soup.find_all('div', class_='product__content')
        for item in products:
            name_tag = item.find('div', class_='product__title')
            name = name_tag.text.strip() if name_tag else 'Unkown Adidas Model'
            both_prices_tag = item.find('div', class_='product__price')
            old_price_tag = both_prices_tag.find('div', class_='price__first')
            old_price_raw = old_price_tag.text.strip()
            current_price_tag = both_prices_tag.find('div', class_='price__sale')
            current_price_raw = current_price_tag.text.strip() if current_price_tag else old_price_raw
            atag = item.find('a', class_='product__info')
            url_path = atag.get('href', '')
            sku = self.extract_sku(url_path)
            list_item = {
                'Model': name,
                'Href': url_path,
                'Sku': sku,
                'Raw_Price': int(re.sub(r"\D", "", current_price_raw)),
                'Raw_Old_Price': int(re.sub(r"\D", "", old_price_raw)) 
            }
            list.append(list_item)

    def view_resource(self, list):
        target_url = "https://www.adidas.ua/choloviki/vzuttya/krosivki/11/big"
        product_selector = ".product__content"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(target_url, wait_until="networkidle")
            page.wait_for_selector(product_selector)
            page_number = 1
            while True:
                page.wait_for_timeout(1000)
                current_products = page.locator(product_selector)
                initial_count = current_products.count()
                current_products.last.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                self.scrab_page(page.content(), list)
                popup_btn = page.locator('div.v-popup__container__close-btn')
                if popup_btn.is_visible():
                    popup_btn.click()
                next_btn = page.locator("div.pagination__item--btn:has-text('Наступна')")
                if next_btn.count() == 0:
                    next_btn = page.locator("div.pagination__item--btn:has-text('>')")
                if next_btn.count() > 0 and next_btn.is_visible():
                    first_product_text_before = current_products.first.inner_text()
                    next_btn.click()
                    try:
                        current_products.first.wait_for(state="visible", timeout=10000)
                        page.wait_for_function("([selector, oldText]) => document.querySelector(selector).innerText !== oldText",
                        arg=[product_selector, first_product_text_before], timeout=10000)
                    except Exception as e:
                        print(e)
                        break
                    page_number += 1
                else:
                    break
            browser.close()