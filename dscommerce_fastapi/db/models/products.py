from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

product_registry = registry()


@product_registry.mapped_as_dataclass
class Product:
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    serial_code: Mapped[str]
    description: Mapped[Optional[str]]
    price: Mapped[float]
    img_url: Mapped[str]
    # category
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=func.now()
    )
    # created_by_id: Mapped[int]
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        init=False, onupdate=func.now()
    )
    # updated_by_id
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        return f'<Product(id={self.id!r}, name={self.name!r}, \
        description={self.description!r}, price={self.price!r}, \
        created_at={self.created_at!r}, updated_at={self.updated_at!r})>'
