from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_expired_after_time(client, user):
    # dentro desse blooc de código, a data de agora vai ser essa,
    # ou seja, datetime.now() retorna o horário definido
    # aqui estamos criando o token
    with freeze_time('2021-01-04 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        response.status_code == HTTPStatus.OK
        token = response.json()['access_token']
    with freeze_time('2021-01-04 12:36:00'):
        # usando o token
        response = client.put(
            f'/users/{user.id}',
            json={
                'username': 'vitor',
                'email': 'vitor@me.com',
                'password': 'secret',
            },
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'wrong_password'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert response.json() == {'detail': 'Incorrect username or password'}


# no curso o username também o email, ficar ligado
def test_token_wrong_username(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'wrong_username', 'password': user.clean_password},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert response.json() == {'detail': 'Incorrect username or password'}


def test_refresh_token(client, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


# se passou do tempo de expiração, não pode dar refresh,
# o usuário tem que fazer login de novo
def test_token_expired_dont_refresh(client, user):
    with freeze_time('2021-01-04 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']
    with freeze_time('2021-01-04 12:36:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
