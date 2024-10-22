from http import HTTPStatus

from tests.factories import OrderFactory, PaymentFactory


def test_create_payment(client, user, token):
    order = OrderFactory(client=user)
    response = client.post(
        '/payments',
        headers={'Authorization': f'Bearer {token}'},
        json={'order_id': order.id},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'message': 'Payment created successfully'}


def test_create_payment_order_not_exist(client, user, token):
    response = client.post(
        '/payments',
        headers={'Authorization': f'Bearer {token}'},
        json={'order_id': 1},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Order not found'}


def test_get_payment(client, user, token):
    order = OrderFactory(client=user)
    payment = PaymentFactory(order=order)
    response = client.get(
        f'/payments/{payment.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': payment.id,
        'moment': payment.moment.isoformat(),
        'order': {
            'id': payment.order.id,
            'status': payment.order.status.value,
            'created_at': payment.order.created_at.isoformat(),
        },
        'client': {
            'id': payment.order.client.id,
            'name': payment.order.client.name,
        },
    }


def test_read_payments(client, user, token):
    order = OrderFactory(client=user)
    order2 = OrderFactory(client=user)
    payment = PaymentFactory(order=order)
    payment2 = PaymentFactory(order=order2)
    response = client.get(
        '/payments',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {
            'id': payment.id,
            'moment': payment.moment.isoformat(),
            'order': {
                'id': payment.order.id,
                'status': payment.order.status.value,
                'created_at': payment.order.created_at.isoformat(),
            },
            'client': {
                'id': payment.order.client.id,
                'name': payment.order.client.name,
            },
        },
        {
            'id': payment2.id,
            'moment': payment2.moment.isoformat(),
            'order': {
                'id': payment2.order.id,
                'status': payment2.order.status.value,
                'created_at': payment2.order.created_at.isoformat(),
            },
            'client': {
                'id': payment2.order.client.id,
                'name': payment2.order.client.name,
            },
        },
    ]
