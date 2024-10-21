from http import HTTPStatus

from pytest import param

from dscommerce_fastapi.db.models.categories import Category
from dscommerce_fastapi.routers.categories import read_categories
from tests.factories import CategoryFactory


def test_create_category(client, user, token):
    response = client.post(
        '/categories',
        json={
            'name': 'test_category',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'test_category',
    }


def test_read_categories(client, user, token):
    category1 = CategoryFactory(created_by=user)
    category2 = CategoryFactory()

    response = client.get(
        '/categories', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'categories': [
            {
                'id': category1.id,
                'name': category1.name,
            },
            {
                'id': category2.id,
                'name': category2.name,
            },
        ]
    }


def test_read_categories_with_name_like(client, user, token):
    category1 = CategoryFactory(created_by=user)
    category2 = CategoryFactory(name='test_category')

    response = client.get(
        '/categories',
        headers={'Authorization': f'Bearer {token}'},
        params={'name': 'test'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'categories': [
            {
                'id': category2.id,
                'name': category2.name,
            },
        ]
    }


def test_update_category(client, user, token):
    category = CategoryFactory(created_by=user)
    response = client.patch(
        f'/categories/{category.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'new name',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': category.id,
        'name': 'new name',
    }


def test_update_category_not_found(client, user, token):
    response = client.patch(
        '/categories/1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'new name',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Category not found',
    }


def test_get_category(client, user, token):
    category = CategoryFactory(created_by=user)
    response = client.get(
        f'/categories/{category.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': category.id,
        'name': category.name,
    }


def test_get_category_not_found(client, user, token):
    response = client.get(
        '/categories/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        'detail': 'Category not found',
    }


def test_delete_category(client, user, token):
    category = CategoryFactory(created_by=user)
    response = client.delete(
        f'/categories/{category.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Category deleted successfully'}
    assert (
        client.get(
            f'/categories/{category.id}',
            headers={'Authorization': f'Bearer {token}'},
        ).status_code
        == HTTPStatus.NOT_FOUND
    )


def test_delete_category_not_found(client, user, token):
    response = client.delete(
        '/categories/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Category not found'}
