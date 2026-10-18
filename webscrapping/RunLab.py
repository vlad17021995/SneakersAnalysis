from playwright.sync_api import sync_playwright
import time
import re
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import re

class RunLab:
    VALID_BRANDS = {
        "NIKE", "ADIDAS", "ASICS", "PUMA", "SAUCONY", 
        "HOKA", "MIZUNO", "MERRELL", "ON", "UNDER ARMOUR", "NEW BALANCE"
    }
    
    def __init__(self):
        pass

    def extract_brand_by_position(self, title_text: str, sku_text: str) -> str:
        if not title_text:
            return "UNKNOWN"
        title = " ".join(title_text.split())
        sku_lower = sku_text.lower().strip() if sku_text else ""
        pattern = r"(?i)\bкросівки\s+([a-zа-яієїґ0-9-]+)(?:\s+([a-zа-яієїґ0-9-]+))?"
        match = re.search(pattern, title)
        potential_brand_word = None

        if match:
            word1 = match.group(1).upper()
            word2 = match.group(2).upper() if match.group(2) else ""
            if word1 in ["NEW", "ON", "UNDER"] and word2 in ["BALANCE", "RUNNING", "ARMOUR"]:
                detected_double = f"{word1} {word2}"
                if word1 == "ON" and word2 == "RUNNING":
                    detected_double = "ON"
                if detected_double in self.VALID_BRANDS:
                    return detected_double
            if word1 in self.VALID_BRANDS:
                return word1

            potential_brand_word = word1

            if re.match(r'^s[0-9]+', sku_lower):
                return "SAUCONY"

            if re.match(r'^[0-9]{7}', sku_lower):
                return "HOKA"
            
            if re.match(r'^[a-z]{1,2}[0-9]{4,5}', sku_lower):
                return "ADIDAS"
            
            if re.match(r'^[0-9]{6}', sku_lower):
                return "PUMA"
            
            if potential_brand_word and potential_brand_word not in ["ENDORPHIN", "CLIFTON", "PEGASUS"]:
                return potential_brand_word
        return "UNKNOWN"

    def extract_sku(self, url_path: str, image_src: str = "") -> str:
        if not url_path:
            return 'None'
        url = url_path.strip().lower()
        url = re.sub(r'\.html\b|\/$', '', url)
    
        if "product_id" not in url:
            url_parts = url.split('_')
            if len(url_parts) > 1:
                potential_sku = url_parts[-1].upper()
                if any(char.isdigit() for char in potential_sku):
                    return potential_sku
        if image_src:
            image_src_lower = image_src.lower()
            image_pattern = r'([a-z0-9]{5,7}-[a-z0-9]{2,3})'
            match = re.search(image_pattern, image_src_lower)
            if match:
                clean_sku = match.group(1).strip('.').upper()
                return clean_sku
        return 'None'

    def check_adv(self, page_):
        dialog = page_.locator("div.cl-dialog")
        if dialog.is_visible():
            close_button = dialog.locator("div.cl-dialog-close-icon")
            if close_button.is_visible():
                close_button.click()
                page_.wait_for_timeout(500)

    def view_resource(self):
        product_selector = ".product-layout.product-grid"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless = False)
            page = browser.new_page()
            page.goto("https://runlab.com.ua/krossovki/size/10-5/11/pol/choloviche/")
            page.wait_for_selector(product_selector)
            while True:
                self.check_adv(page)
                current_products = page.locator(product_selector)
                initial_count = current_products.count()
                last_product = current_products.last
                last_product.scroll_into_view_if_needed()
                new_items_loaded = False
                for _ in range(6):
                    time.sleep(0.5)
                    self.check_adv(page)
                    last_product.scroll_into_view_if_needed()
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
            image_tag = item.find('div', class_='image')
            image_src = image_tag.find('a').find('img').get('src', '')
            try:
                name_tag = item_tag.find('h2', class_='product-name').find('a')
                if name_tag:
                    name = name_tag.text.strip()
                    href = name_tag.get('href', '')
                    sku = self.extract_sku(href, image_src)
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
                brand = self.extract_brand_by_position(name, sku)

                list_item = {
                    'brand': brand,
                    'model_name': name,
                    'sku': sku,
                    'marketplace': 'runlab.com.ua',
                    'url': href,
                    'price': int(re.sub(r"\D", "", current_price_raw)),
                    'old_price': int(re.sub(r"\D", "", old_price_raw))
                }
                list_result.append(list_item)
            except Exception as error:
                print({ error })
                continue
        return list_result