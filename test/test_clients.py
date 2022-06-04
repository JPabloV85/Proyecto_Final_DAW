import pytest
from app import create_app
from test import get_auth_headers, get_apikey_headers


@pytest.fixture
def client():
    app = create_app('config_tests.py')

    with app.test_client() as client:
        yield client


##
# Client endpoints

def test_clientClaim(client):
    headers = get_auth_headers(client, "pablo", "alberti")

    jsonData = {"idBet": 1, "reward": 10}
    rv = client.patch('/api/client/claim', headers=headers, follow_redirects=True, json=jsonData)
    rsp = rv.get_json()
    assert isinstance(rsp.get("new_cash"), float)


def test_clientMyBalance(client):
    headers = get_auth_headers(client, "pablo", "alberti")

    rv = client.get('/api/client/my_balance', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and isinstance(rsp.get("cash"), float) and isinstance(rsp.get("image"), str)


def test_clientProfile(client):
    headers = get_auth_headers(client, "pablo", "alberti")

    rv = client.get('/api/client/profile', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and rsp.get("id") == 1 \
           and isinstance(rsp.get("cif"), str) \
           and rsp.get("user").get("username") == "pablo"


##
# Admin endpoints

def test_getClient(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/client/Client/58744698C', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 1

    rv = client.get('/api/client/Client/876543C', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_deleteClient(client):
    headers = get_apikey_headers("alberti")

    rv = client.delete('/api/client/Client/58744698C', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("user").get("username") == "pablo"

    # Refered user gets deleted too
    rv = client.get('/api/user/User/pablo', headers=headers, follow_redirects=True)
    assert rv.status_code == 404

    rv = client.get('/api/client/Client/876543C', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_putClient(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/client/Client/58744698C', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rsp.get("id") == 1 \
           and rsp.get("user").get("username") == "pablo" \
           and rsp.get("user").get("email") == "pablo@a.a"

    formData = {"Username": "antonio", "E-mail": "antonio@a.a"}

    rv = client.put('/api/client/1', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and rsp.get("id") == 1 \
           and rsp.get("user").get("username") == "antonio" \
           and rsp.get("user").get("email") == "antonio@a.a"

    rv = client.put('/api/client/5', headers=headers, follow_redirects=True, data=formData)
    assert rv.status_code == 404


def test_getClientList(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/client', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 2


def test_postClient(client):
    headers = get_apikey_headers("alberti")

    formData = {"Username": "antonio", "CIF": "123456V", "E-mail": "antonio@a.a", "Password": "alberti"}

    rv = client.post('/api/client/', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("user").get("username") == "antonio" \
           and rsp.get("user").get("email") == "antonio@a.a" \
           and rsp.get("number_of_bets") == 0
