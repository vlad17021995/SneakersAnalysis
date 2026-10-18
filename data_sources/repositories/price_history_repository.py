from data_sources.entities.base import DBConnection
from data_sources.entities import MarketPlace, Brand, Model, URL, PriceHistory, FlatPriceView
import pandas as pd
from datetime import datetime

class PriceHistoryRepository:
    def __init__(self, db_connection: DBConnection):
        self.db = db_connection
        self.db.create_tables()
    
    def get_all_flat_prices_as_objects(self):
        session = self.db.get_session()
        try:
            return session.query(FlatPriceView).all()
        finally:
            session.close()

    def get_all_flat_prices_for_pandas(self) -> pd.DataFrame:
        query = 'SELECT * FROM v_flat_prices'
        df = pd.read_sql(query, self.db.engine)
        return df
    
    def save_scrapped_item(self, item: dict):
        session = self.db.get_session()
        try:
            mp = session.query(MarketPlace).filter_by(name=item['marketplace'].lower()).first()
            if not mp:
                mp = MarketPlace(name=item['marketplace'].lower())
                session.add(mp)
                session.flush()
            brand = session.query(Brand).filter_by(name=item['brand'].upper()).first()
            if not brand:
                brand = Brand(name=item['brand'].upper())
                session.add(brand)
                session.flush()
            model = session.query(Model).filter_by(sku=item['sku'].upper()).first()
            if not model:
                model = Model(name=item['model_name'], sku=item['sku'].upper(), id_brand=brand.id_brand)
                session.add(model)
                session.flush()
            url_entry = session.query(URL).filter_by(link=item['url']).first()
            if not url_entry:
                url_entry = URL(link=item['url'], id_model=model.id_model, id_marketplace=mp.id_marketplace)
                session.add(url_entry)
                session.flush()
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            existing_price_today = (
                session.query(PriceHistory).filter(
                    PriceHistory.id_model == model.id_model,
                    PriceHistory.id_marketplace == mp.id_marketplace,
                    PriceHistory.timestamp >= today_start
                )
                .first()
            )
            if existing_price_today:
                existing_price_today.price = item['price']
                existing_price_today.old_price = item.get('old_price')
                existing_price_today.timestamp = datetime.now() # оновлюємо час
            else:
                price_log = PriceHistory(
                id_model=model.id_model,
                id_marketplace=mp.id_marketplace,
                price=item['price'],
                old_price=item.get('old_price'))            
                session.add(price_log)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()