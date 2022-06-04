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

def test_getRole(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/role/Role/admin', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 2 and rsp.get("name") == "admin"

    rv = client.get('/api/role/Role/developer', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_deleteRole(client):
    headers = get_apikey_headers("alberti")

    rvAdminUser = client.get('/api/user/User/pedro', headers=headers, follow_redirects=True)
    rspAdminUser = rvAdminUser.get_json()
    assert rvAdminUser.status_code == 200 and {"name": "admin"} in rspAdminUser.get("roles")

    rvRole = client.delete('/api/role/Role/admin', headers=headers, follow_redirects=True)
    rspRole = rvRole.get_json()
    rvAdminUser = client.get('/api/user/User/pedro', headers=headers, follow_redirects=True)
    rspAdminUser = rvAdminUser.get_json()
    assert rvRole.status_code == 200 \
           and rspRole.get("id") == 2 \
           and {"name": "admin"} not in rspAdminUser.get("roles")  # Role gets removed from User.roles

    rv = client.delete('/api/role/Role/developer', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_putRole(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/role/Role/admin', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rsp.get("id") == 2 and rsp.get("name") == "admin"

    formData = {"Name": "developer"}

    rv = client.put('/api/role/2', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rsp.get("id") == 2 and rsp.get("name") == "developer"

    rv = client.put('/api/role/25', headers=headers, follow_redirects=True, data=formData)
    assert rv.status_code == 404


def test_getRoleList(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/role', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 2


def test_postHorse(client):
    headers = get_apikey_headers("alberti")

    # Existing Stud
    formData = {"Name": "developer"}

    rv = client.post('/api/role/', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("name") == "developer"
