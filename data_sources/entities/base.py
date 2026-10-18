from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

class Base(DeclarativeBase):
    pass

class DBConnection:
    def __init__(self, db_url: str = 'sqlite:///running_prices.db'):
        self.engine = create_engine(db_url, echo=False)
        self.SessionFactory = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        Base.metadata.create_all(self.engine)
        drop_query = 'DROP VIEW IF EXISTS v_flat_prices;'
        view_query = """
            CREATE VIEW IF NOT EXISTS v_flat_prices AS
            SELECT 
                ph.id_pricehistory,
                b.name AS brand_name,
                m.name AS model_name,
                m.sku,
                mp.name AS marketplace_name,
                u.link AS url,
                ph.price,
                ph.old_price,
                ph.timestamp
            FROM price_history ph
            JOIN models m ON ph.id_model = m.id_model
            JOIN brands b ON m.id_brand = b.id_brand
            JOIN marketplaces mp ON ph.id_marketplace = mp.id_marketplace
            JOIN urls u ON u.id_model = m.id_model AND u.id_marketplace = mp.id_marketplace;
            """
        with self.engine.connect() as conn:
            conn.execute(text(drop_query))
            conn.execute(text(view_query))
            conn.commit()

    def get_session(self):
        return self.SessionFactory()