# Tentei criar essa classe de associação no ManyToMany, mas, por algum motivo o alembic não detecta e cria a tabela, ver dps

# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html

# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from dscommerce_fastapi.db import Base
# from dscommerce_fastapi.db.models.categories import Category
# from dscommerce_fastapi.db.models.products import Product


# class ProductCategory(Base):
#     __tablename__ = 'product_category'

#     id: Mapped[int] = mapped_column(primary_key=True)

#     # Foreign Keys

#     product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
#     category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

#     product: Mapped['Product'] = relationship(back_populates='categories')
#     category: Mapped['Category'] = relationship(back_populates='products')
