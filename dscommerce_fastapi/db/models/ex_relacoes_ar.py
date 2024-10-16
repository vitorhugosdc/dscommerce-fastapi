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
