from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_sources.entities.base import Base

class MarketPlace(Base):
    __tablename__ = 'marketplaces'
    id_marketplace: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    urls: Mapped[List['URL']] = relationship(back_populates='marketplace')
    prices: Mapped[List['PriceHistory']] = relationship(back_populates='marketplace')