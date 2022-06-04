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

def test_Available(client):
    headers = get_auth_headers(client, "pablo", "alberti")

    rv = client.get('/api/run/available', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) > 0


##
# Admin endpoints

def test_getRun(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/run/Run/20JUN-01', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("date") == "20/06/2022" \
           and len(rsp.get("horses")) == 5

    rv = client.get('/api/run/Run/78KMN-09', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_deleteRun(client):
    headers = get_apikey_headers("alberti")

    rv = client.delete('/api/run/Run/20JUN-01', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and isinstance(rsp.get("id"), int)

    rv = client.delete('/api/run/Run/45VXC-12', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_putRun(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/run/Run/20JUN-01', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rsp.get("id") == 2 \
           and rsp.get("date") == "20/06/2022" \
           and rsp.get("time") == "16:00" \
           and len(rsp.get("horses")) == 5

    formData = {"Date": "30/05/2022", "Remove Horse (equineID)": "B12345"}
    rv = client.put('/api/run/2', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rsp.get("id") == 2 \
           and rsp.get("date") == "30/05/2022" \
           and rsp.get("time") == "16:00" \
           and len(rsp.get("horses")) == 4

    formData = {"Time": "17:30", "Add Horse (equineID)": "B12345"}
    rv = client.put('/api/run/2', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rsp.get("id") == 2 \
           and rsp.get("date") == "30/05/2022" \
           and rsp.get("time") == "17:30" \
           and len(rsp.get("horses")) == 5

    formData = {"Date": "30052022"}
    rv = client.put('/api/run/2', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 500 and "Incorrect date format" in rsp

    formData = {"Time": "30-22"}
    rv = client.put('/api/run/2', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 500 and "Incorrect time format" in rsp

    rv = client.put('/api/run/150', headers=headers, follow_redirects=True, data=formData)
    assert rv.status_code == 404


def test_getRunList(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/run', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 25


def test_postRun(client):
    headers = get_apikey_headers("alberti")

    formData = {"Tag": "22JUN-01", "Date": "22/06/2022", "Time": "16:00"}

    rv = client.post('/api/run/', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("tag") == "22JUN-01" \
           and rsp.get("date") == "22/06/2022" \
           and rsp.get("time") == "16:00"

    formData = {"Tag": "22JUN-02", "Date": "22022", "Time": "16:00"}

    rv = client.post('/api/run/', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 500 and "Incorrect date format" in rsp

    formData = {"Tag": "22JUN-03", "Date": "22/06/2022", "Time": "160"}

    rv = client.post('/api/run/', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 500 and "Incorrect time format" in rsp
