from playwright.sync_api import sync_playwright
import time
import re
import numpy as np
from bs4 import BeautifulSoup

class Epicentr:
    def __init__(self):
        pass

    def extract_sku(self, title_text: str) -> str:
        if not title_text:
            return 'None'
        title = title_text.replace("s/n", "")
        title = ' '.join(title_text.split()).lower()
        brackets_match = re.search(r'\((s?[0-9a-z-]+)\s+([0-9a-z.]+)\)', title)
        if brackets_match:
            part1 = brackets_match.group(1)
            part2 = brackets_match.group(2)
            if "р." in title:
                size_match = re.search(r'р\.\s*([0-9,.]+)', title)
                if size_match and size_match.group(1).replace(',', '.') == part2.replace(',', '.'):
                    return part1.upper()
            if len(part2) > 1 and not part2.replace('.', '').isdigit():
                return f"{part1}-{part2}".upper()
            elif len(part2) >= 2 and len(part1) <= 6: 
                return f"{part1}-{part2}".upper()
        title = title.replace("s/n", "")
        hoka_fix_pattern = r'\b([0-9]{7}[a-z]?)\s+([a-z0-9]{2,5})\b(?=.*р\.\s*[0-9])'
        title = re.sub(hoka_fix_pattern, r'\1-\2', title)
        hoka_match = re.search(r'\b([0-9]{7}[a-z]?-[a-z0-9]{2,5})\b', title)
        if hoka_match:
            return hoka_match.group(1).upper()
        #title = re.sub(r'\b([0-9]{7})\s+([a-z0-9]{2,4})\s+(?=р\.\s*[0-9])', r'\1-\2 ', title)
        anchor_pattern = r"(?:\s|^)([a-z0-9_-]+)\s+р\.\s*[0-9]"
        match = re.search(anchor_pattern, title)
        if match:
            return match.group(1).upper()
        return 'None'
    
    def view_resource(self):
        list_result = []
        search_queries = [
            # 1. Загальні брендові запити (дають найбільше покриття, але вимагають фільтрації в коді)
            "Nike Pegasus", "Nike Vomero", "Nike Zoom", "Nike Winflo", "Nike Vaporfly", "Nike Structure", 
            "Nike Zegama", "Nike Alphafly", "Nike Streakfly", "Adidas SUPERNOVA", "Adidas adizero", 
            "Adidas PUREBOOST", "Adidas DURAMO", "Adidas ULTRABOOST", "Adidas HYPERBOOST", "Adidas TERREX", 
            "Asics SUPERBLAST", "Asics GEL-CUMULUS", "Asics GEL-PULSE", "Asics NOVABLAST", "Asics GEL-EXCITE", 
            "Asics GEL-NIMBUS", "Asics DYNABLAST", "Asics NOOSA TRI", "Asics MAGIC SPEED", "Asics METASPEED", 
            "Asics GT", "Asics VERSABLAST", "Asics SONICBLAST", "Asics GEL-KAYANO", "Asics TRABUCO", "Puma Nitro", 
            "New Balance", #"New Balance 520", "New Balance FuelCell", "New Balance Fresh Foam", "New Balance MMORLC6", 
            "Saucony", "Hoka", "On Running"  # Пошук On через точні моделі, щоб уникнути сміття "Slip-on"
        ]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            for req in search_queries:
                self.search_model(req, list_result, page)
            browser.close()
        return list_result

    def search_model(self, req, list_result, page):
        target_url = "https://epicentrk.ua/ua/search/?q=" + req + "&SECTION_ID=5419"
        if req == "New Balance":
            target_url = "https://epicentrk.ua/ua/shop/krosivky/fs/brend-new-balance/pryznachennia-dlia-bihu/"
        if req == "Hoka":
            target_url = "https://epicentrk.ua/ua/brands/hoka.html?SECTION_ID=5419"
        if req == "On Running":
            target_url = "https://epicentrk.ua/ua/shop/krosivky/fs/brend-on/"
        product_selector = "._7d58lFfz"
        page_control_selector = "._A1s-wYY9"
        page.goto(target_url)
        page.wait_for_selector(product_selector)
        page.wait_for_load_state("networkidle")
        while True:
            current_products = page.locator(product_selector)
            initial_count = current_products.count()
            last_product = current_products.last
            html_content = page.content()
            self.fill_out_list(html_content, list_result)
            last_product.scroll_into_view_if_needed()
            if not last_product.get_attribute("itemscope"):
                break
            controls = page.locator(page_control_selector)
            if controls.count() == 0:
                break
            next_button = controls.last.locator('a')
            if next_button:
                next_button.click()
            else:
                break
        
    def fill_out_list(self, content, list_result):
        soup = BeautifulSoup(content, 'html.parser')
        products = soup.find_all('div', class_='_BiSUwK5l')
        for item in products:
            try:
                avaliable = item.find('div', class_='_duYDToPT')
                if avaliable:
                    break
                name_tag = item.find('div', class_='_R59CWAgb').find('a')
                if name_tag:
                    name = name_tag.text.strip() 
                    url_path = name_tag.get('href', '')
                    full_title = name_tag.get('title', '') or name_tag.get_text(strip=True)
                    sku = self.extract_sku(full_title)
                else:
                    name = "Unknown Model"
                    url_path = ''
                    full_title = ''
                    sku = ''
                both_prices_tag = item.find('div', class_='_hFNrWMyR')
                current_price_raw = 0 
                old_price_raw = 0
                if not both_prices_tag.find('div', class_='_oUaq5aIu'):
                    current_price_raw = old_price_raw = both_prices_tag.find('div', class_='_Al-5uY1o').find('data').find('data').get_text()
                else:
                    current_price_raw = both_prices_tag.find('div', class_='_oUaq5aIu').find('s').find('data').get_text()
                    old_price_raw = both_prices_tag.find('div', class_='_Al-5uY1o').find('data').find('data').get_text()
                list_item = {
                    'Model': name,
                    'Title': full_title,
                    'Sku': sku,
                    'Raw_Price': int(re.sub(r"\D", "", current_price_raw)),
                    'Raw_Old_Price': int(re.sub(r"\D", "", old_price_raw)) 
                }
                print(list_item)
                list_result.append(list_item)
            except Exception as error:
                print({ error })
                continue