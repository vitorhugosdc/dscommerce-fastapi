from http import HTTPStatus

from sqlalchemy import select

from dscommerce_fastapi.db.models.products import Product
from tests.conftest import ProductFactory
from tests.factories import CategoryFactory


def test_create_product(client, token):
    category = CategoryFactory()

    response = client.post(
        '/products',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'name',
            'serial_code': 'code',
            'description': 'description',
            'price': 100,
            'img_url': 'url',
            'categories_ids': [
                category.id,
            ],
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        # precisou fazer assim pois a CategoryFactory cria um produto, ai ele pega o id 1
        # mas verificar a logica, pois na teoria teria que ser indice 1, pois o product 1 ja tá em category
        'id': category.products[0].id,
        'name': 'name',
        'serial_code': 'code',
        'description': 'description',
        'price': 100.0,
        'img_url': 'url',
        'categories': [
            {
                'id': category.id,
                'name': category.name,
            }
        ],
    }


def test_create_product_already_exists(client, token):
    product = ProductFactory()
    category = CategoryFactory()

    response = client.post(
        '/products',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'name',
            'serial_code': product.serial_code,
            'description': 'description',
            'price': 100,
            'img_url': 'url',
            'categories_ids': [
                category.id,
            ],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Product already exists'}


def test_create_product_category_not_exists(client, token):
    response = client.post(
        '/products',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'name',
            'serial_code': 'code',
            'description': 'description',
            'price': 100,
            'img_url': 'url',
            'categories_ids': [
                1,
            ],
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Category not found'}


def test_read_products(client, token):
    product = ProductFactory()
    product2 = ProductFactory()

    response = client.get(
        '/products', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            'id': product.id,
            'name': product.name,
            'serial_code': product.serial_code,
            'description': product.description,
            'price': product.price,
            'img_url': product.img_url,
            'categories': [
                {'id': category.id, 'name': category.name}
                for category in product.categories
            ],
        },
        {
            'id': product2.id,
            'name': product2.name,
            'serial_code': product2.serial_code,
            'description': product2.description,
            'price': product2.price,
            'img_url': product2.img_url,
            'categories': [
                {'id': category.id, 'name': category.name}
                for category in product2.categories
            ],
        },
    ]


def test_update_product(client, user, token):
    product = ProductFactory(created_by=user)
    category = CategoryFactory()
    response = client.patch(
        f'/products/{product.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'new name',
            'serial_code': 'new code',
            'description': 'new description',
            'price': 200,
            'img_url': 'new url',
            'categories_ids': [category.id],
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': product.id,
        'name': 'new name',
        'serial_code': 'new code',
        'description': 'new description',
        'price': 200.0,
        'img_url': 'new url',
        'categories': [
            {
                'id': product.categories[0].id,
                'name': product.categories[0].name,
            },
            {
                'id': category.id,
                'name': category.name,
            },
        ],
    }


def test_update_product_category_not_exists(client, user, token):
    product = ProductFactory(created_by=user)
    response = client.patch(
        f'/products/{product.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'new name',
            'serial_code': 'new code',
            'description': 'new description',
            'price': 200,
            'img_url': 'new url',
            # se passar categoria que não existe ele não da erro, pela maneira que foi feito
            # ele meio que só ignora mesmo
            'categories_ids': [2],
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': product.id,
        'name': 'new name',
        'serial_code': 'new code',
        'description': 'new description',
        'price': 200.0,
        'img_url': 'new url',
        'categories': [
            {
                # como categoria 2 não existe, o esperado é que tenha só a que já tinha
                'id': product.categories[0].id,
                'name': product.categories[0].name,
            }
            # for category in product.categories
        ],
    }


def test_get_product(client, token):
    category = CategoryFactory()
    product = ProductFactory(categories=[category])
    # product.categories.append(category)

    response = client.get(
        f'/products/{product.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': product.id,
        'name': product.name,
        'serial_code': product.serial_code,
        'description': product.description,
        'price': product.price,
        'img_url': product.img_url,
        'categories': [
            {
                'id': product.categories[0].id,
                'name': product.categories[0].name,
            }
        ],
    }


def test_delete_product(session, client, user, token):
    product = ProductFactory(created_by=user)
    response = client.delete(
        f'/products/{product.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Product deleted successfully'}
    assert (
        session.scalars(
            select(Product).where(Product.id == product.id, Product.is_active)
        ).one_or_none()
        is None
    )
    # apenas maneiras diferentes de fazer a mesma coisa que acima
    assert (
        session.scalar(
            select(Product).where(Product.id == product.id, Product.is_active)
        )
        is None
    )
    assert (
        session.query(Product)
        .filter(Product.id == product.id, Product.is_active)
        .first()
        is None
    )
    assert (
        session.scalar(
            select(Product).filter(Product.id == product.id, Product.is_active)
        )
        is None
    )


def test_delete_product_user_didnt_create_product(client, token):
    product = ProductFactory()
    response = client.delete(
        f'/products/{product.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Product not found'}
