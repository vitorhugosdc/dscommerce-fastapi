from http import HTTPStatus

from tests.conftest import ProductFactory


def test_create_product(client, token):
    response = client.post(
        '/products',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'name',
            'serial_code': 'code',
            'description': 'description',
            'price': 100,
            'img_url': 'url',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'name',
        'serial_code': 'code',
        'description': 'description',
        'price': 100,
        'img_url': 'url',
    }


def test_read_products(session, client, token):
    expected_products = 5
    session.bulk_save_objects(ProductFactory.create_batch(expected_products))
    session.commit()

    response = client.get(
        '/products', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == expected_products
