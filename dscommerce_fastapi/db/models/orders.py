from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dscommerce_fastapi.db import Base
from dscommerce_fastapi.db.models.payment import Payment

if TYPE_CHECKING:
    from dscommerce_fastapi.db.models.products import (
        Product,
    )
    from dscommerce_fastapi.db.models.users import User

OrderProductAssociation = Table(
    'order_product',
    Base.metadata,
    Column('order_id', ForeignKey('orders.id'), primary_key=True),
    Column('product_id', ForeignKey('products.id'), primary_key=True),
)


class Order(Base):
    class OrderStatus(Enum):
        WAITING_PAYMENT = 'WAITING_PAYMENT'
        PAID = 'PAID'
        SHIPPED = 'SHIPPED'
        DELIVERED = 'DELIVERED'
        CANCELED = 'CANCELED'

    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus]
    created_at: Mapped[datetime] = mapped_column(
        default=func.now()
    )  # moment do diagrama
    # removi updated_at e removed_at pois pra mim não faz sentido apagar ou modificar um pedido já pronto com exceção do status dele

    # Foreign Keys

    client_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    # Relationships

    # orders é o nome do atributo lá em Product
    products: Mapped[List['Product']] = relationship(
        secondary=OrderProductAssociation, back_populates='orders'
    )

    client: Mapped['User'] = relationship(
        back_populates='orders', foreign_keys=[client_id]
    )
    # não tem payment_id aqui pois em One-To-One, a gente coloca
    # chave estrangeira somente na tabela filha, apontando pra pai,
    # como Order é pai de Payment, a gente coloca order_id em payment
    # e aqui deixa só a relação
    payment: Mapped[Optional['Payment']] = relationship(
        back_populates='order',
    )
