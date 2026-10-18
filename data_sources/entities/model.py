from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_sources.entities.base import Base

class Model(Base):
    __tablename__ = 'models'
    id_model: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), nullable=False)
    id_brand: Mapped[int] = mapped_column(ForeignKey("brands.id_brand"))
    brand: Mapped["Brand"] = relationship(back_populates="models")
    urls: Mapped[List['URL']] = relationship(back_populates='model')
    prices: Mapped[List['PriceHistory']] = relationship(back_populates='model')