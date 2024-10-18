import factory.fuzzy
import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import create_database, database_exists, drop_database

from dscommerce_fastapi.app import app
from dscommerce_fastapi.database import get_session
from dscommerce_fastapi.db import Base
from dscommerce_fastapi.security import get_password_hash
from tests.factories import CategoryFactory, ProductFactory, UserFactory

# class UserFactory(factory.Factory):
#     class Meta:
#         model = User

#     name = factory.Faker('name')
#     # username = factory.Sequence(lambda n: f'user{n}')
#     username = factory.Faker('user_name')
#     # email = factory.LazyAttribute(lambda obj: f'{obj.usernamen}@test.com')
#     email = factory.Faker('email')
#     phone = factory.Faker('phone_number')
#     password = factory.LazyAttribute(lambda obj: f'{obj.username}+senha')
#     # password = get_password_hash('testtest')


# class ProductFactory(factory.Factory):
#     class Meta:
#         model = Product

#     name = factory.Faker('name')
#     serial_code = factory.Sequence(lambda n: f'code{n}')
#     description = factory.Faker('sentence')
#     price = factory.fuzzy.FuzzyDecimal(0, 1000, precision=2)
#     img_url = factory.Faker('url')


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
        echo=False,  # Echo é pra printar a criação das tabelas, etc, mas mais importante, as consultas
    )
    # if database_exists(engine.url):
    #     drop_database(engine.url)
    # create_database(engine.url)

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine, autocommit=False, autoflush=False
    )

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    UserFactory._meta.sqlalchemy_session = session
    ProductFactory._meta.sqlalchemy_session = session
    CategoryFactory._meta.sqlalchemy_session = session

    nested = connection.begin_nested()

    @sqlalchemy.event.listens_for(session, 'after_transaction_end')
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session
    session.close()
    transaction.rollback()
    connection.close()


# fixture para que se for passado user como parametro, ele vai ter um objeto
# User dentro dele  inserido no banco de dados
# pode ser assim ou fazer mais proximo do rodrigo, ou seja,
# inserindo os usuários via POST no Arrange/Preparação dos testes
# Esse User é um objeto do SQLAlchemy
@pytest.fixture
def user(session):
    pwd = 'testtest'
    # user = UserFactory(password=get_password_hash(pwd))
    user = UserFactory(password=pwd)
    session.add(user)
    session.commit()
    session.refresh(user)
    # user.clean_password = pwd
    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Tive que adicionar user como parametro pois se não ele criava outro usuário
@pytest.fixture
def token(client, user):
    # user = UserFactory(password=get_password_hash('testtest'))
    # user = UserFactory(password='testtest')
    response = client.post(
        '/auth/token',
        # data={'username': user.username, 'password': user.clean_password},
        data={'username': user.username, 'password': user.password},
    )
    return response.json()['access_token']


# @pytest.fixture
# def product(session):
#     product = ProductFactory()
#     session.add(product)
#     session.commit()
#     session.refresh(product)
#     return product
