import pytest
import requests
from pydantic import ValidationError
from fastapi_pagination import Page

from presentation.viewmodels.models import Token, ProductsRead, ClientsRead, OrdersRead, OrderProductLink

def test_bad_request_no_credentials_get_token():

    url = 'http://localhost:8000/users/login'
    response = requests.post(url)

    assert response.status_code == 400

def test_get_token():

    url = 'http://localhost:8000/users/login?login=jorge&password=jorge'
    response = requests.post(url)

    assert response.status_code == 200

    try:

        response_data = response.json()
        valid_data = Token(**response_data)

    except ValidationError:

        pytest.fail('Response data validation error!')

    assert valid_data.token_type == 'Bearer'
    assert valid_data.access_token != None

def test_get_wrong_login_token():

    url = 'http://localhost:8000/users/login?login=jorg&password=123'
    response = requests.post(url)

    assert response.status_code == 400

    response_data = response.json()
    body = dict(**response_data)

    assert body['detail'] == 'Credenciais incorretas!'

def test_get_wrong_password_token():

    url = 'http://localhost:8000/users/login?login=jorge&password=1234'
    response = requests.post(url)

    assert response.status_code == 400

    response_data = response.json()
    body = dict(**response_data)

    assert body['detail'] == 'Credenciais incorretas!'

def test_get_products():

    url = 'http://localhost:8000/users/login?login=jorge&password=jorge'
    response = requests.post(url)

    assert response.status_code == 200


    response_data = response.json()
    token = Token(**response_data)

    url = f'http://localhost:8000/products/?access_token={token.access_token}&token_type=Bearer&page=1&size=50'
    response = requests.get(url)

    assert response.status_code == 200

    try:

        response_data = response.json()
        valid_data = Page[ProductsRead].parse_obj(response_data)

    except ValidationError:

        pytest.fail('Response data validation error!')

    assert valid_data.items[0].id != None