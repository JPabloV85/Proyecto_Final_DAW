import pytest
from app import create_app
from test import get_apikey_headers


@pytest.fixture
def client():
    app = create_app('config_tests.py')

    with app.test_client() as client:
        yield client


##
# Admin endpoints

def test_getStud(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/stud/1', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("name") == "El Chaparral"

    rv = client.get('/api/stud/gf', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_deleteStud(client):
    headers = get_apikey_headers("alberti")

    rv = client.delete('/api/stud/1', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 1 and rsp.get("name") == "El Chaparral"

    # Horses from that stud get deleted too
    rv = client.get('/api/horse/Horse/A12345', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_putStud(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/stud/1', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rsp.get("id") == 1 \
           and rsp.get("name") == "El Chaparral" \
           and rsp.get("location") == "Cádiz"

    formData = {"Name": "Nuevo Chaparral", "Location": "Chiclana"}
    rv = client.put('/api/stud/1', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rsp.get("id") == 1 \
           and rsp.get("name") == "Nuevo Chaparral" \
           and rsp.get("location") == "Chiclana"

    rv = client.put('/api/stud/25', headers=headers, follow_redirects=True, data=formData)
    assert rv.status_code == 404


def test_getStudList(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/stud', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 3


def test_postHorse(client):
    headers = get_apikey_headers("alberti")

    formData = {"Name": "El Picadero", "Location": "Bormujos de la Frontera", "E-mail": "erpicaero@javiapruebame.com"}

    rv = client.post('/api/stud', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("name") == "El Picadero" \
           and rsp.get("location") == "Bormujos de la Frontera" \
           and rsp.get("email") == "erpicaero@javiapruebame.com"
