from datetime import datetime
from http import HTTPStatus

from freezegun import freeze_time

from tests.factories import ProductFactory


def test_create_order(client, user):
    product1 = ProductFactory()
    product2 = ProductFactory()

    with freeze_time('2021-01-04 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.password},
        )
        assert response.status_code == HTTPStatus.OK
        response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2021-01-04 12:00:00'):
        response = client.post(
            '/orders',
            json={'products_ids': [product1.id, product2.id]},
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'status': 'WAITING_PAYMENT',
        'created_at': '2021-01-04 12:00:00',
        'client': {
            'id': user.id,
            'name': user.name,
        },
        'products': [
            {
                'id': product1.id,
                'name': product1.name,
            },
            {
                'id': product2.id,
                'name': product2.name,
            },
        ],
        'payment': None,
    }


# class OrderRead(BaseModel):
#     id: int
#     status: Order.OrderStatus
#     created_at: datetime
#     client: UserRead
#     products: list[ProductRead]
#     payment: PaymentRead | None
