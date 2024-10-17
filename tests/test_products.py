from http import HTTPStatus

from dscommerce_fastapi.routers import categories
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


def test_read_products(session, client, token):
    expected_products = 5
    products = ProductFactory.create_batch(expected_products)

    response = client.get(
        '/products', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == expected_products


def test_get_product(client, token):
    category = CategoryFactory()
    product = ProductFactory()
    product.categories.append(category)

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
