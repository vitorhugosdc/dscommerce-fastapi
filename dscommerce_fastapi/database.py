from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dscommerce_fastapi.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


# o comentário ao lado da definição da função serve para ser ignorado
# nos testes, ai não interfere no coverage de testes,
# pois é uma função que não pode ser coberta por testes
def get_session():  # pragma: no cover
    # é tipo try with resources do Java, ele cria a sessão
    # e fecha automaticamente,
    #  por isso não precisa de um session.close()
    # basicamente, essa função vai executar até o yield,
    # ai vai voltar lá nas funções que o chamaram,
    # e após executar elas, retorna para cá e finaliza a sessão automaticamente
    with Session(engine) as session:
        yield session
