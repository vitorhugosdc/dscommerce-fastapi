from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dscommerce_fastapi.db import Base
from dscommerce_fastapi.db.models.products import Product
from dscommerce_fastapi.db.models.users import User


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    # Foreign Keys

    created_by_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('users.id')
    )
    deleted_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('users.id')
    )

    # Relationships

    products: Mapped[List['Product']] = relationship(back_populates='category')

    created_by: Mapped['User'] = relationship(foreign_keys=[created_by_id])
    updated_by: Mapped[Optional['User']] = relationship(
        foreign_keys=[updated_by_id]
    )
    deleted_by: Mapped[Optional['User']] = relationship(
        foreign_keys=[deleted_by_id]
    )
