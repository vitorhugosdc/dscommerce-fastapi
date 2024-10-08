from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from dscommerce_fastapi.db.models.products import Product

category_registry = registry()


@category_registry.mapped_as_dataclass
class Category:
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        init=False, onupdate=func.now()
    )

    # Relationships
    products: Mapped[List['Product']] = relationship(
        'Product', back_populates='category'
    )
