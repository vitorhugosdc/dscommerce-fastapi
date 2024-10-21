from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dscommerce_fastapi.db import Base

if TYPE_CHECKING:
    from dscommerce_fastapi.db.models.orders import Order


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    moment: Mapped[datetime] = mapped_column(default=func.now())

    # Foreign Keys

    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))

    # Relationships

    order: Mapped['Order'] = relationship(back_populates='payment')
