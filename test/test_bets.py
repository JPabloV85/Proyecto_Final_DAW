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

def test_mybets(client):
    headers = get_auth_headers(client, "pablo", "alberti")

    rv = client.get('/api/bet/my_bets', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert len(rsp) == 4

    headers = get_auth_headers(client, "maria", "alberti")

    rv = client.get('/api/bet/my_bets', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert len(rsp) == 0


def test_client_newBet(client):
    headers = get_auth_headers(client, "pablo", "alberti")

    jsonData = {"horse_id": 1, "race_id": 1, "bet_position": 1, "bet_amount": 10, "benefit_ratio": 2}
    rv = client.post('/api/bet/client_new_bet', headers=headers, follow_redirects=True, json=jsonData)
    rsp = rv.get_json()
    assert isinstance(rsp.get("new_cash"), float)


##
# Admin endopoints

def test_getBet(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/bet/1', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 1

    rv = client.get('/api/bet/20', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_deleteBet(client):
    headers = get_apikey_headers("alberti")

    rv = client.delete('/api/bet/1', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 1

    rv = client.delete('/api/bet/20', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_getBetList(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/bet/client/pablo', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 4

    rv = client.get('/api/bet/client/manuel', headers=headers, follow_redirects=True)
    assert rv.status_code == 404
