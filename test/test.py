import pytest
from app import create_app
from werkzeug.datastructures import Headers


@pytest.fixture
def client():
    app = create_app('config_tests.py')

    with app.test_client() as client:
        yield client


def get_auth_headers(client, username, password):
    rv = client.post('/login', json={'username': username, 'password': password})
    rsp = rv.get_json()
    headers = Headers()
    headers.add('Authorization', f"Bearer {rsp['access_token']}")
    return headers


def get_apikey_headers(apikey):
    headers = Headers()
    headers.add('Authorization', apikey)
    return headers


def test_prueba(client):
    rv = client.get('/')
    assert "<title>Admin Login</title>" in rv.get_data(as_text=True)


def test_login(client):
    rv = client.post('/login', json={'username': 'pablo', 'password': 'alberti'})
    rsp = rv.get_json()
    assert 'access_token' in rsp.keys()
