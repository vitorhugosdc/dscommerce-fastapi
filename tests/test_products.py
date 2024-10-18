from http import HTTPStatus

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
            'categories_ids': [2],
        },
    )

    assert response.json() == {'detail': 'Category not found'}
    assert response.status_code == HTTPStatus.NOT_FOUND


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


def test_delete_product(client, user, token):
    product = ProductFactory(created_by=user)
    response = client.delete(
        f'/products/{product.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Product deleted successfully'}


def test_delete_product_user_didnt_create_product(client, token):
    product = ProductFactory()
    response = client.delete(
        f'/products/{product.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Product not found'}
