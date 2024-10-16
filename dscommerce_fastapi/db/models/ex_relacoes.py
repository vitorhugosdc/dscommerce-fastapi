# -------------------------------1 pra N-------------------------

# class Product(Base):
#     ...
#     created_by_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

#     created_by: Mapped['User'] = relationship(
#             #products_created_by lá em User
#             back_populates='products_created_by',
#             # precisa desse argumento, pois como created_by e updated_by se referem
#             # a mesma chave primária na tabela users, tem que definir qual é qual
#             foreign_keys=[created_by_id],
#         )

#     updated_by_id: Mapped[Optional[int]] = mapped_column(
#         ForeignKey('users.id')
#     )

#     updated_by: Mapped[Optional['User']] = relationship(
#         #products_updated_by lá em User
#         back_populates='products_updated_by',
#         foreign_keys=[updated_by_id],
#     )
# ------------------------------------------------------------------------------
# class User(Base):
#     ...
#     products_created_by: Mapped[List['Product']] = relationship(
#         back_populates='created_by',
#         foreign_keys='Product.created_by_id',
#     )
#     products_updated_by: Mapped[List['Product']] = relationship(
#         back_populates='updated_by',
#         foreign_keys='Product.updated_by_id',
#     )
