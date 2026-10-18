from webscrapping import Puma, Saucony, RunLab, NewBalance, Adidas, ArenaStore, Epicentr
from data_sources.entities.base import DBConnection
from data_sources.repositories.price_history_repository import PriceHistoryRepository
import pandas as pd
import csv
import itertools

def main():
    db_conn = DBConnection("sqlite:///running_prices.db")
    repo = PriceHistoryRepository(db_conn)
    adidas_list = []
    adidas_obj = Adidas()
    adidas_obj.view_resource(adidas_list)
    arenastore_obj = ArenaStore()
    arenastore_list = arenastore_obj.view_resource()
    epicentr_obj = Epicentr()
    epicentr_list = epicentr_obj.view_resource()
    newbalance_obj = NewBalance()
    newbalance_list = newbalance_obj.view_resource()
    runlab_obj = RunLab()
    runlab_list = runlab_obj.view_resource()
    saucony_obj = Saucony()
    saucony_list = saucony_obj.view_resource()
    puma_obj = Puma()
    puma_list = puma_obj.view_resource()

    for item in itertools.chain(adidas_list, arenastore_list, epicentr_list, newbalance_list, runlab_list, saucony_list, puma_list):
        repo.save_scrapped_item(item)
    db_from_db = repo.get_all_flat_prices_for_pandas()
    db_from_db.to_csv('backup_dump.csv', index=False, encoding='utf-8-sig')

    """
    try:
        raw_csv_df = pd.read_csv("backup_dump.csv")
        for index, row in raw_csv_df.iterrows():
            # Перетворюємо рядок таблиці назад у плоский словник для вашого репозиторію
            flat_item = {
                "brand": row["brand_name"],
                "model_name": row["model_name"],
                "sku": row["sku"],
                "marketplace": row["marketplace_name"],
                "url": row["url"],
                "price": float(row["price"]),
                "old_price": float(row["old_price"]) if pd.notna(row["old_price"]) else None
            }
            # Ваш репозиторій сам розкидає цей рядок по 5 таблицях!
            repo.save_scraped_item(flat_item)
    except FileNotFoundError:
        pass
    """
    
    """
    with open('puma.csv', 'w', newline='', encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=['Model',
                    'Sku', 'Raw_Price', 'Raw_Old_Price'])
        writer.writeheader()
        writer.writerows(puma_list)
    """
    #processed_items = []
    #with open('epicentr_data.csv', mode='r', encoding='utf-8-sig') as infile:
    #    reader = csv.DictReader(infile)
    #    for row in reader:
    #        title = row.get('Title', '') or row.get('title', '')
    #        new_sku = extract_sku(title)
    #        processed_items.append({
    #            'Title': title,
    #            'Sku': new_sku
    #        })
    #with open('proc_epicentr_data.csv', mode='w', newline='', encoding='utf-8-sig') as outfile:
    #    writer = csv.DictWriter(outfile, fieldnames=['Title', 'Sku'])
    #    writer.writeheader()
    #    writer.writerows(processed_items)

if __name__ == "__main__":
    main()