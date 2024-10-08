from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from dscommerce_fastapi.db.models.categories import Category
from dscommerce_fastapi.db.models.users import User

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
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        init=False, onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    # Foreign keys

    created_by_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    updated_by_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id'), nullable=False, index=True
    )

    # Relationships (relationships não são salvos no banco de dados,
    # são apenas para definir a relação entre as tabelas)

    created_by: Mapped['User'] = relationship(
        'User', back_populates='products_created_by'
    )
    updated_by: Mapped['User'] = relationship(
        'User', back_populates='products_updated_by'
    )

    # products é o nome do atributo lá na Category
    category: Mapped[Category] = relationship(
        'Category', back_populates='products'
    )

    def __repr__(self):
        return f'<Product(id={self.id!r}, name={self.name!r}, \
        description={self.description!r}, price={self.price!r}, \
        created_at={self.created_at!r}, updated_at={self.updated_at!r})>'
