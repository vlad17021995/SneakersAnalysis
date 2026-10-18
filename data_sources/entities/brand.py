from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_sources.entities.base import Base

class Brand(Base):
    __tablename__ = 'brands'
    id_brand: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    models: Mapped[list['Model']] = relationship(back_populates='brand')