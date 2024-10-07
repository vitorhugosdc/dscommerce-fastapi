from http import HTTPStatus

from jwt import decode

from dscommerce_fastapi.security import create_access_token, settings


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)

    result = decode(token, settings.SECRET_KEY, settings.ALGORITHM)

    assert result['sub'] == data['sub']
    assert result['exp']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer invalid'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_invalid_user(client, token):
    response = client.delete('/users/2', headers={'Authorization': f'{token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    assert response.json() == {'detail': 'Not authenticated'}
