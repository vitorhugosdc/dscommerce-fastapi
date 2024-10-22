from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dscommerce_fastapi.db.models.order_item import OrderItem
from dscommerce_fastapi.db.models.orders import Order

if TYPE_CHECKING:
    from dscommerce_fastapi.db.models.categories import Category
from dscommerce_fastapi.db import Base
from dscommerce_fastapi.db.models.users import User

# Tabela de associação Many-To-Many entre Product e Category
ProductCategoryAssociation = Table(
    'product_category',
    Base.metadata,
    Column('product_id', ForeignKey('products.id'), primary_key=True),
    Column('category_id', ForeignKey('categories.id'), primary_key=True),
)


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    serial_code: Mapped[str]
    description: Mapped[Optional[str]]
    price: Mapped[float]
    img_url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    # Foreign keys

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), index=True
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('users.id'), index=True
    )
    deleted_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('users.id'), index=True
    )

    # # não precisa do nullable se colocar Optional igual no arbo, deixei pra exemplo
    # category_id: Mapped[int] = mapped_column(
    #     ForeignKey('categories.id'), nullable=False, index=True
    # )

    # Relationships (relationships não são salvos no banco de dados,
    # são apenas para definir a relação entre as tabelas)

    created_by: Mapped['User'] = relationship(
        # poderia tirar o 'User', pois ele já pega de 'User' acima,
        # deixei para exemplo 'User',
        # back_populates é pra uma relação bidirecional, ou seja,
        # pro sqlalchemy saber que, se atualizar User,
        # atualiza Product ou Products relacionados a ele já na hora...
        # a gente coloca na string o nome do ATRIBUTO lá na outra classe,
        # ou seja, products_created_by lá em User
        # back_populates='products_created_by',
        # A gente precisa definir foreign_keys pois, como created_by,
        # updated_by e removed_by se referem
        # a mesma chave primária na tabela users, tem que definir qual é qual
        foreign_keys=[created_by_id],
    )
    updated_by: Mapped[Optional['User']] = relationship(
        # updated_by_id é o atributo aqui da classe mesmo
        foreign_keys=[updated_by_id],
    )
    deleted_by: Mapped[Optional['User']] = relationship(
        # removed_by_id é o atributo aqui da classe mesmo
        foreign_keys=[deleted_by_id],
    )

    # -------- Many-To-Many entre Product e Category com tabela intermediária, sem atributos extras --------

    # products é o nome do atributo lá na Category
    categories: Mapped[List['Category']] = relationship(
        secondary=ProductCategoryAssociation, back_populates='products'
    )

    # -------- fim Many-To-Many entre Product e Category com tabela intermediária, sem atributos extras --------

    # -------- Many-To-Many entre Order e product com tabela intermediária e atributos extras --------
    orders: Mapped[Optional[List['Order']]] = relationship(
        secondary='order_item', back_populates='products'
    )

    order_products_association: Mapped[List['OrderItem']] = relationship(
        # product é o nome do atributo lá em OrderItem
        back_populates='product',
    )

    # -------- fim Many-To-Many entre Order e product com tabela intermediária e atributos extras --------

    def __repr__(self):
        return f'<Product(id={self.id!r}, name={self.name!r}, \
        description={self.description!r}, price={self.price!r}, \
        created_at={self.created_at!r}, updated_at={self.updated_at!r})>'
