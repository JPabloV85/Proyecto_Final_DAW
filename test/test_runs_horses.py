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

def test_getParticipants(client):
    headers = get_auth_headers(client, "pablo", "alberti")

    jsonData = {"race_id": 1}
    rv = client.post('/api/run_horse/getParticipants', headers=headers, follow_redirects=True, json=jsonData)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 5 and any(h['horse_name'] == 'Rocinante' for h in rsp)


##
# Admin endpoints

def test_getRunHorse(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/run_horse/20JUN-01', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 2 and len(rsp.get("horses")) == 5

    rv = client.get('/api/run_horse/51DEC-01', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_getRunHorseList(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/run_horse', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 25


def test_putRunHorse(client):
    headers = get_apikey_headers("alberti")

    formData = {"Run Tag": "30JUN-01", "Horse(equineID)": "A12345", "Position": 1}
    rv = client.put('/api/run_horse', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert "Run not found" in rsp and rv.status_code == 404

    formData = {"Run Tag": "20JUN-01", "Horse(equineID)": "F12345", "Position": 1}
    rv = client.put('/api/run_horse', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert "Horse not found" in rsp and rv.status_code == 404

    formData = {"Run Tag": "20JUN-01", "Horse(equineID)": "E12345", "Position": 1}
    rv = client.put('/api/run_horse', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert "not participating" in rsp and rv.status_code == 404

    formData = {"Run Tag": "20JUN-01", "Horse(equineID)": "B12345", "Position": 1}
    rv = client.put('/api/run_horse', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp == "Horse B12345 final position set to: 1"
