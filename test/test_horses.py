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

def test_Horse(client):
    headers = get_auth_headers(client, "pablo", "alberti")

    rv = client.get('/api/horse/detail/3', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert isinstance(rsp.get("id"), int) \
           and rsp.get("name") == "Gamora" \
           and rsp.get("age") == 10 \
           and rsp.get("stud").get("location") == "Madrid" \
           and rsp.get("timesFirst") == 2
    rv = client.get('/api/horse/detail/5', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert isinstance(rsp.get("id"), int) \
           and rsp.get("name") == "Furia" \
           and rsp.get("age") == 7 \
           and rsp.get("stud").get("location") == "Sevilla" \
           and rsp.get("timesFirst") == 0

    rv = client.get('/api/horse/detail/30', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


##
# Admin endpoints

def test_getHorse(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/horse/Horse/C54321', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 3 and rsp.get("name") == "Gamora"

    rv = client.get('/api/horse/Horse/F0987654', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_deleteHorse(client):
    headers = get_apikey_headers("alberti")

    rv = client.delete('/api/horse/Horse/C54321', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 3

    rv = client.delete('/api/horse/Horse/F23947642', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_putHorse(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/horse/Horse/C54321', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rsp.get("id") == 3 \
           and rsp.get("name") == "Gamora" \
           and rsp.get("age") == 10 \
           and rsp.get("stud").get("name") == "Hnos. Díaz"

    formData = {"Name": "Nebula", "Age": 12, "New Stud (name)": "Torreluna"}

    rv = client.put('/api/horse/3', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rsp.get("id") == 3 \
           and rsp.get("name") == "Nebula" \
           and rsp.get("age") == 12 \
           and rsp.get("stud").get("name") == "Torreluna"

    rv = client.put('/api/horse/25', headers=headers, follow_redirects=True, data=formData)
    assert rv.status_code == 404


def test_getHorseList(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/horse', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 10


def test_postHorse(client):
    headers = get_apikey_headers("alberti")

    # Existing Stud
    formData = {"EquineID": "F12345", "Name": "Thanos", "Breed": "Appaloosa", "Age": 15, "Stud Name": "Torreluna"}

    rv = client.post('/api/horse/', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("name") == "Thanos" \
           and rsp.get("breed") == "Appaloosa" \
           and rsp.get("stud").get("name") == "Torreluna"

    # Non-existing Stud
    formData = {"EquineID": "F54321", "Name": "Thanos", "Breed": "Appaloosa", "Age": 15, "Stud Name": "Titán",
                "Stud Location": "Saturno", "Stud E-mail": "saturno@universe.com"}

    rv = client.post('/api/horse/', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("name") == "Thanos" \
           and rsp.get("breed") == "Appaloosa" \
           and rsp.get("stud").get("name") == "Titán" \
           and rsp.get("stud").get("location") == "Saturno"
