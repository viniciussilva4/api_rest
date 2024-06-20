import pytest
import requests
from pydantic import ValidationError
from fastapi_pagination import Page

from presentation.viewmodels.models import Token, ProductsRead, ClientsRead, OrdersRead

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
    assert valid_data.items[0].price_of_sell != None
    assert valid_data.items[0].bar_code != None
    assert valid_data.items[0].section != None
    assert valid_data.items[0].initial_inventory != None
    assert valid_data.items[0].expiration_date != None
    assert valid_data.items[0].image != None

def test_get_product():

    url = 'http://localhost:8000/users/login?login=jorge&password=jorge'
    response = requests.post(url)

    assert response.status_code == 200


    response_data = response.json()
    token = Token(**response_data)

    url = f'http://localhost:8000/products/2?access_token={token.access_token}&token_type=Bearer'
    response = requests.get(url)

    assert response.status_code == 200

    try:

        response_data = response.json()
        valid_data = ProductsRead(**response_data)

    except ValidationError:

        pytest.fail('Response data validation error!')

    assert valid_data.id != None
    assert valid_data.price_of_sell != None
    assert valid_data.bar_code != None
    assert valid_data.section != None
    assert valid_data.initial_inventory != None
    assert valid_data.expiration_date != None
    assert valid_data.image != None

def test_get_clients():

    url = 'http://localhost:8000/users/login?login=jorge&password=jorge'
    response = requests.post(url)

    assert response.status_code == 200


    response_data = response.json()
    token = Token(**response_data)

    url = f'http://localhost:8000/clients/?access_token={token.access_token}&token_type=Bearer&page=1&size=50'
    response = requests.get(url)

    assert response.status_code == 200

    try:

        response_data = response.json()
        valid_data = Page[ClientsRead].parse_obj(response_data)

    except ValidationError:

        pytest.fail('Response data validation error!')

    assert valid_data.items[0].id != None
    assert valid_data.items[0].name != None
    assert valid_data.items[0].cpf != None
    assert valid_data.items[0].email != None

def test_get_client():

    url = 'http://localhost:8000/users/login?login=jorge&password=jorge'
    response = requests.post(url)

    assert response.status_code == 200


    response_data = response.json()
    token = Token(**response_data)

    url = f'http://localhost:8000/clients/2?access_token={token.access_token}&token_type=Bearer&page=1&size=50'
    response = requests.get(url)

    assert response.status_code == 200

    try:

        response_data = response.json()
        valid_data = ClientsRead(**response_data)

    except ValidationError:

        pytest.fail('Response data validation error!')

    assert valid_data.id != None
    assert valid_data.name != None
    assert valid_data.cpf != None
    assert valid_data.email != None

def test_get_orders():

    url = 'http://localhost:8000/users/login?login=jorge&password=jorge'
    response = requests.post(url)

    assert response.status_code == 200


    response_data = response.json()
    token = Token(**response_data)

    url = f'http://localhost:8000/orders/?access_token={token.access_token}&token_type=Bearer&page=1&size=50'
    response = requests.get(url)

    assert response.status_code == 200

    try:

        response_data = response.json()
        valid_data = Page[OrdersRead].parse_obj(response_data)

    except ValidationError:

        pytest.fail('Response data validation error!')

    assert valid_data.items[0].id != None
    assert valid_data.items[0].period != None
    assert valid_data.items[0].products_section != None
    assert valid_data.items[0].status != None
    assert valid_data.items[0].products != None
    assert valid_data.items[0].products[0].id != None
    assert valid_data.items[0].products[0].order_id != None
    assert valid_data.items[0].products[0].product_id != None
    assert valid_data.items[0].products[0].quantity != None

def test_get_order():

    url = 'http://localhost:8000/users/login?login=jorge&password=jorge'
    response = requests.post(url)

    assert response.status_code == 200


    response_data = response.json()
    token = Token(**response_data)

    url = f'http://localhost:8000/orders/2?access_token={token.access_token}&token_type=Bearer&page=1&size=50'
    response = requests.get(url)

    assert response.status_code == 200

    try:

        response_data = response.json()
        valid_data = OrdersRead(**response_data)

    except ValidationError:

        pytest.fail('Response data validation error!')

    assert valid_data.id != None
    assert valid_data.period != None
    assert valid_data.products_section != None
    assert valid_data.status != None
    assert valid_data.products != None
    assert valid_data.products[0].id != None
    assert valid_data.products[0].order_id != None
    assert valid_data.products[0].product_id != None
    assert valid_data.products[0].quantity != None