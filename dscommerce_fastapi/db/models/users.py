from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dscommerce_fastapi.db import Base
from dscommerce_fastapi.db.models.orders import Order

if TYPE_CHECKING:
    # from dscommerce_fastapi.db.models.categories import Category
    from dscommerce_fastapi.db.models.products import Product
from dscommerce_fastapi.db.models.orders import Order


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    # Optional significa que é opcional no banco de dados e,
    # se não for informado será Nulo | None
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships

    orders: Mapped[Optional[List['Order']]] = relationship(
        back_populates='client'
    )

    # Acho que talvez não precisa ter esse relacionamento?
    # Pois Não quero de user acessar seus produtos criados,
    # como no arbo que tem referencia ao User mas não o inverso?

    # Na verdade, coloca somente se quiser uma relação bidirectional, se não,
    # deixa só lá em products mesmo,
    # oq nesse caso faz sentido deixar somente lá mesmo
    # no caso, user é Pai de Product, então ele não deve armazenar id,
    # mas nesse caso mais específico ele só deve ter a relação, no máximo

    # products_created_by: Mapped[List['Product']] = relationship(
    #     'Product',
    #     back_populates='created_by',
    #     foreign_keys='Product.created_by_id',
    # )
    # products_updated_by: Mapped[List['Product']] = relationship(
    #     'Product',
    #     back_populates='updated_by',
    #     foreign_keys='Product.updated_by_id',
    # )

    def __repr__(self):
        return f'<User(id={self.id!r}, name={self.name!r}, \
        username={self.username!r}, email={self.email!r}, \
        created_at={self.created_at!r}, updated_at={self.updated_at!r})>'
