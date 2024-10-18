import factory
import factory.fuzzy

from dscommerce_fastapi.db.models.categories import Category
from dscommerce_fastapi.db.models.products import Product
from dscommerce_fastapi.db.models.users import User

factory.Faker._DEFAULT_LOCALE = 'pt_BR'


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = 'flush'

    id = factory.Sequence(lambda n: n)
    name = factory.Faker('name')
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}+senha')
    created_at = factory.Faker('date_time')


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Category
        sqlalchemy_session_persistence = 'flush'

    id = factory.Sequence(lambda n: n)
    name = factory.Faker('name')
    created_at = factory.Faker('date_time')

    # products = factory.RelatedFactoryList(
    #     'tests.factories.ProductFactory',
    #     'categories',
    #     size=2,
    # )

    created_by = factory.SubFactory(UserFactory)


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Product
        sqlalchemy_session_persistence = 'flush'

    id = factory.Sequence(lambda n: n)
    name = factory.Faker('name')
    serial_code = factory.Sequence(lambda n: f'code{n}')
    description = factory.Faker('sentence')
    price = factory.fuzzy.FuzzyFloat(0, 1000, precision=2)
    img_url = factory.Faker('url')
    created_at = factory.Faker('date_time')

    categories = factory.List([
        factory.SubFactory(CategoryFactory),
    ])

    created_by = factory.SubFactory(UserFactory)
