from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dscommerce_fastapi.db import Base

if TYPE_CHECKING:
    from dscommerce_fastapi.db.models.orders import Order
    from dscommerce_fastapi.db.models.products import Product


# Tabela de associação com atributos extras (quantity) então é diferente do Table definido lá em Product
class OrderItem(Base):
    __tablename__ = 'order_item'

    order_id: Mapped[int] = mapped_column(
        ForeignKey('orders.id'), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id'), primary_key=True
    )
    quantity: Mapped[int]

    order: Mapped['Order'] = relationship(
        back_populates='order_products_association'
    )
    product: Mapped['Product'] = relationship(
        back_populates='order_products_association'
    )
