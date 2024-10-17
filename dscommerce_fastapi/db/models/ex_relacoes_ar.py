# ----------------------------------------1 pra N--------------------------------
# Classe que é o N:

#     removed_by_id: Mapped[Optional[int]] = mapped_column(
#         #users.id é a tabela users atributo id (chave primária)
#         ForeignKey("users.id"), index=True
#     )

#      # relationships
#     removed_by: Mapped[Optional[User]] = relationship(
#         foreign_keys=[removed_by_id]
#     )

# Classe que é o 1:


# ----------------------------------------N pra N--------------------------------

# Tabela intermediária:
# class ProductCategory(Base):
#     __tablename__ = 'product_category'

#     id: Mapped[int] = mapped_column(primary_key=True)

#     # Foreign Keys

#     product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
#     category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

# #    # products é o nome do atributo lá na Category
#     categories: Mapped[List['Category']] = relationship(
#         secondary='product_category', back_populates='products'
#     )

# class Product:

#     # products é o nome do atributo lá na Category
#     categories: Mapped[List['Category']] = relationship(
#         secondary='product_category', back_populates='products'
#     )

# class Category:

#     products: Mapped[List['Product']] = relationship(
#         secondary='product_category', back_populates='categories'
#     )
