from sqlalchemy import Column, Integer, String, Float, DateTime, text
from data_sources.entities.base import Base
from datetime import datetime

class FlatPriceView(Base):
    __tablename__ = 'v_flat_price'
    id_pricehistory = Column(Integer, primary_key=True)
    brand_name = Column(String)
    model_name = Column(String)
    sku = Column(String)
    marketplace_name = Column(String)
    url = Column(String)
    price = Column(Float)
    old_price = Column(Float)
    timestamp = Column(DateTime)
    __table_args__ = {'extend_existing': True}