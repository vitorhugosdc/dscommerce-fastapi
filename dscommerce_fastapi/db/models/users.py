from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dscommerce_fastapi.db import Base

if TYPE_CHECKING:
    # from dscommerce_fastapi.db.models.categories import Category
    from dscommerce_fastapi.db.models.products import Product


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships

    products_created_by: Mapped[List['Product']] = relationship(
        'Product',
        back_populates='created_by',
        foreign_keys='Product.created_by_id',
    )
    products_updated_by: Mapped[List['Product']] = relationship(
        'Product',
        back_populates='updated_by',
        foreign_keys='Product.updated_by_id',
    )

    def __repr__(self):
        return f'<User(id={self.id!r}, name={self.name!r}, \
        username={self.username!r}, email={self.email!r}, \
        created_at={self.created_at!r}, updated_at={self.updated_at!r})>'
