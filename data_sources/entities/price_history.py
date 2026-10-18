from typing import List
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_sources.entities.base import Base

class PriceHistory(Base):
    __tablename__ = 'price_history'
    id_pricehistory: Mapped[int] = mapped_column(primary_key=True)
    id_model: Mapped[int] = mapped_column(ForeignKey("models.id_model"))
    id_marketplace: Mapped[int] = mapped_column(ForeignKey("marketplaces.id_marketplace"))
    price: Mapped[float] = mapped_column(nullable=False)
    old_price: Mapped[float] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now, index=True)
    model: Mapped['Model'] = relationship(back_populates="prices")
    marketplace: Mapped['MarketPlace'] = relationship(back_populates="prices")
