from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        init=False, onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        return f'<User(id={self.id!r}, name={self.name!r}, \
        username={self.username!r}, email={self.email!r}, \
        created_at={self.created_at!r}, updated_at={self.updated_at!r})>'
