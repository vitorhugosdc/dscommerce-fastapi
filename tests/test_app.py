from http import HTTPStatus


def test_read_root_must_return_ok_and_hello_world(client):
    # client = TestClient(app)  # Arrange

    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # assert
    assert response.json() == {'message': 'Hello World!'}
    response.json().get('message') == 'Hello World!'
