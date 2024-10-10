import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from dscommerce_fastapi.app import app
from dscommerce_fastapi.database import get_session
from dscommerce_fastapi.db.models.products import Product
from dscommerce_fastapi.db.models.users import User
from dscommerce_fastapi.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.Faker('name')
    # username = factory.Sequence(lambda n: f'user{n}')
    username = factory.Faker('user_name')
    # email = factory.LazyAttribute(lambda obj: f'{obj.usernamen}@test.com')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}+senha')
    # password = get_password_hash('testtest')


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    name = factory.Faker('name')
    serial_code = factory.Sequence(lambda n: f'code{n}')
    description = factory.Faker('sentence')
    price = factory.fuzzy.FuzzyDecimal(0, 1000, precision=2)
    img_url = factory.Faker('url')


# fixture para não ter que criar o TestCliente toda vez,
# então passamos ela como parametro para todos os testes
# e ele já vai saber que toda vez que tiver o parametro chamado cliente,
# é para executar essa função, passando o retorno dela pro nosso teste
# agora, passa a ser uma fixture que depende de outra fixture, a session
@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        # isso é especifico do sqlite, onde não pode rodar objetos sqlite em
        # threads diferentes, então settamos para não verificar mais
        connect_args={'check_same_thread': False},
        # não crie várias validaçoes de banco de dados, garanta que tudo vai
        # rodar de forma estática
        poolclass=StaticPool,
    )

    # cria todas as tabelas dos models que estão registrados como
    # @table_registry.mapped_as_dataclass, como o model User por exemplo
    # user_registry.metadata.create_all(engine)
    # product_registry.metadata.create_all(engine)
    # category_registry.metadata.create_all(engine)

    with Session(engine) as session:
        # yield transforma a Session em um gerador, a fixture vai rodar até o
        # yield
        # e depois vai parar de executar
        # o objeto que foi dado yield (session) é o que vai parar lá dentro do
        #  teste, como parametro session
        # basicamente, até o yield é tudo o que vai ser feito antes do teste,
        # depois dele é o teardown, ou seja, tudo que vc fez, desfaça

        # assistir aula sobre yield, playlist de geradores e corrotinas
        # aula 151 pra frente

        yield session

    # após todos os testes, dropa as tabelas criadas
    user_registry.metadata.drop_all(engine)
    product_registry.metadata.drop_all(engine)
    category_registry.metadata.drop_all(engine)


# fixture para que se for passado user como parametro, ele vai ter um objeto
# User dentro dele  inserido no banco de dados
# pode ser assim ou fazer mais proximo do rodrigo, ou seja,
# inserindo os usuários via POST no Arrange/Preparação dos testes
# Esse User é um objeto do SQLAlchemy
@pytest.fixture
def user(session):
    pwd = 'testtest'
    user = UserFactory(password=get_password_hash(pwd))
    session.add(user)
    session.commit()
    session.refresh(user)
    user.clean_password = pwd
    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture
def product(session):
    product = ProductFactory()
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
