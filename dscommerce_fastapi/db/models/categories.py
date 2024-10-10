from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dscommerce_fastapi.db import Base
from dscommerce_fastapi.db.models.products import Product


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())

    # Relationships
    products: Mapped[List['Product']] = relationship(
        'Product', back_populates='category'
    )
