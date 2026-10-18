from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_sources.entities.base import Base

class URL(Base):
    __tablename__ = 'urls'
    id_url: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    id_model: Mapped[int] = mapped_column(ForeignKey("models.id_model"))
    id_marketplace: Mapped[int] = mapped_column(ForeignKey("marketplaces.id_marketplace"))
    model: Mapped['Model'] = relationship(back_populates="urls")
    marketplace: Mapped['MarketPlace'] = relationship(back_populates="urls")