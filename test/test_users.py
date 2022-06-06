from io import BytesIO
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

def test_register(client):
    imageLocalPath = client.application.root_path + "/test/"
    imageName = "carnet.jpg"
    with open(imageLocalPath + imageName, 'rb') as image:
        imageData = {"image": (BytesIO(image.read()), imageName)}

    formData = {"username": "ana", "nif": "234239V", "email": "ana@a.a", "password": "alberti",
                "image": imageData["image"]}
    rv = client.post('/api/user/register', follow_redirects=True, content_type='multipart/form-data', data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 201 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("user").get("username") == "ana"


def test_update(client):
    headersPatch = get_auth_headers(client, "pablo", "alberti")
    headersGet = get_apikey_headers("alberti")

    rv = client.get('/api/user/User/pablo', headers=headersGet, follow_redirects=True)
    rsp = rv.get_json()
    assert rsp.get("id") == 1 \
           and rsp.get("username") == "pablo" \
           and rsp.get("email") == "pablo@a.a"

    # Test update username and email for non-existing ones (no image update)
    imageLocalPath = client.application.root_path + "/test/"
    imageName = "mifoto.jpg"
    with open(imageLocalPath + imageName, 'rb') as image:
        imageData = {"image": (BytesIO(image.read()), "")}

    formData = {"username": "ana", "email": "ana@a.a", "password": "alberti", "image": imageData["image"]}
    rv = client.patch('/api/user/update', headers=headersPatch, follow_redirects=True,
                      content_type='multipart/form-data', data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 201 \
           and rsp.get("id") == 1 \
           and rsp.get("user").get("username") == "ana" \
           and rsp.get("user").get("email") == "ana@a.a"

    # Test update username for existing one (no image update)
    imageLocalPath = client.application.root_path + "/test/"
    imageName = "mifoto.jpg"
    with open(imageLocalPath + imageName, 'rb') as image:
        imageData = {"image": (BytesIO(image.read()), "")}

    formData = {"username": "pedro", "email": "pablo@a.a", "password": "alberti", "image": imageData["image"]}
    rv = client.patch('/api/user/update', headers=headersPatch, follow_redirects=True,
                      content_type='multipart/form-data', data=formData)
    assert rv.status_code == 500


##
# Admin endpoints

def test_getUser(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/user/User/pablo', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("id") == 1 and rsp.get("email") == "pablo@a.a"

    rv = client.get('/api/user/User/spiderman', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_deleteClient(client):
    headers = get_apikey_headers("alberti")

    rv = client.delete('/api/user/User/pablo', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and rsp.get("username") == "pablo"

    # Refered client gets deleted too
    rv = client.get('/api/client/Client/58744698C', headers=headers, follow_redirects=True)
    assert rv.status_code == 404

    rv = client.delete('/api/user/User/spiderman', headers=headers, follow_redirects=True)
    assert rv.status_code == 404


def test_putUser(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/user/User/pablo', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rsp.get("id") == 1 \
           and rsp.get("email") == "pablo@a.a" \
           and {"name": "client"} in rsp.get("roles")

    formData = {"Username": "antonio", "E-mail": "antonio@a.a", "Add Role": "admin"}

    rv = client.put('/api/user/1', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and rsp.get("id") == 1 \
           and rsp.get("username") == "antonio" \
           and rsp.get("email") == "antonio@a.a"\
           and {"name": "admin"} in rsp.get("roles")

    rv = client.put('/api/user/5', headers=headers, follow_redirects=True, data=formData)
    assert rv.status_code == 404


def test_getUserList(client):
    headers = get_apikey_headers("alberti")

    rv = client.get('/api/user', headers=headers, follow_redirects=True)
    rsp = rv.get_json()
    assert rv.status_code == 200 and len(rsp) == 3


def test_postUser(client):
    headers = get_apikey_headers("alberti")

    formData = {"Username": "antonio", "CIF": "123456V", "E-mail": "antonio@a.a", "Password": "alberti", "Add Role": "admin"}

    rv = client.post('/api/user/', headers=headers, follow_redirects=True, data=formData)
    rsp = rv.get_json()
    assert rv.status_code == 200 \
           and isinstance(rsp.get("id"), int) \
           and rsp.get("username") == "antonio" \
           and rsp.get("email") == "antonio@a.a" \
           and {"name": "admin"} in rsp.get("roles")
