from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from typing import Optional
from datetime import date
import re

from application.products_service import ProductsService
from application.users_service import UsersService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import Products, ProductsRead, ProductsUpdate
from presentation.viewmodels.models import Users
from security.validators import verify_role, verify_status

engine = get_engine()

router = APIRouter()
prefix = '/products'

products_service = ProductsService()
users_service = UsersService()


def get_ordering(atributes: Optional[str] = None, order: Optional[str] = None):

    if atributes == None or order == None:

        return None

    atributes = atributes.split(',')

    order = order.split(',')

    if len(atributes) != len(order):

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Requisição mal realizada!')
    
    order_params = []

    try:
    
        for index in range(len(atributes)):

            if order[index].strip() != 'asc' and order[index].strip() != 'desc':

                raise AttributeError
            
            elif order[index].strip() == 'asc':

                order_params.append(asc(getattr(Products, atributes[index].strip())))

            else:

                order_params.append(desc(getattr(Products, atributes[index].strip())))

    except AttributeError:

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Requisição mal realizada!')

    return order_params


@router.get('/', status_code = status.HTTP_200_OK, response_model = Page[ProductsRead])
async def get_products(current_user: Users = Depends(users_service.get_current_user), 
                       ordering = Depends(get_ordering), 
                       section: Optional[str] = Query(None), 
                       bar_code: Optional[str] = Query(None), 
                       min_price_of_sell: Optional[float] = Query(None), 
                       max_price_of_sell: Optional[float] = Query(None), 
                       min_initial_inventory: Optional[int] = Query(None), 
                       max_initial_inventory: Optional[int] = Query(None), 
                       min_expiration_date: Optional[date] = Query(None), 
                       max_expiration_date: Optional[date] = Query(None)):
    
    """
    Retorna uma pagina com uma lista de todos os produtos.
    
    - **items**: lista de produtos
    - **id**: id do produto
    - **price_of_sell**: preço de venda do produto
    - **bar_code**: código de barras do produto
    - **section**: seção do produto
    - **initial_inventory**: quantidade em estoque do produto
    - **expiration_date**: data de validade do produto
    - **image**: imagem do produto

    - **total**: total de itens
    - **page**: pagina atual da requisição
    - **size**: quantidade de itens por página
    - **pages**: quantidade de páginas

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e o `token_type` obtidos no login para que a requisição seja realizada.

    - *Organização:*
    - O `atributes` deve ser uma sequência de caracteres(string) separados 
    por vírgula, em formato de lista, dos atributos que se desejar usar para organizar a requisição.
    É opcional, mas deve estar de acordo com o `order`, na mesma quantidades de parâmetros.
    - O `order` deve ser uma sequência de caracteres(string) separados 
    por vírgula, em formato de lista, dos fatores de organização 'asc' / 'desc' que se desejar usar para organizar a requisição.
    É opcional, mas deve estar de acordo com o `atributes`, na mesma quantidades de parâmetros.

    - *Filtros:*
    - O `section` deve ser uma sequência de caracteres(string), da seção que se deseja filtrar. 
    É opcional.
    - O `bar_code` deve ser uma sequência de caracteres(string), do código de barras que se deseja filtrar. 
    É opcional, mas se preenchido deve ter 13 caracteres de números.
    - O `min_price_of_sell` deve ser uma sequência de caracteres(string), do menor preço desejado.
    É opcional, mas se preenchido deve ter até 2 casas decimais e 10 casas antes da vírgula de números.
    - O `max_price_of_sell` deve ser uma sequência de caracteres(string), do maior preço desejado.
    É opcional, mas se preenchido deve ter até 2 casas decimais e 10 casas antes da vírgula de número.
    - O `min_initial_inventory` deve ser uma sequência de caracteres(string), do menor estoque desejado.
    É opcional, mas se preenchido deve ser apenas números.
    - O `max_initial_inventory` deve ser uma sequência de caracteres(string), do maior estoque desejado.
    É opcional, mas se preenchido deve ser apenas números.
    - O `min_expiration_date` deve ser uma sequência de caracteres(string), da menor data de validade desejado.
    É opcional, mas se preenchido deve estar no formato AAAA-MM-DD como 2024-06-20, por exemplo.
    - O `max_expiration_date` deve ser uma sequência de caracteres(string), da maior data de validade desejado.
    É opcional, mas se preenchido deve estar no formato AAAA-MM-DD como 2024-06-20, por exemplo.

    **Casos de Uso**:

    - Listar todos os produtos cadastrados.

    **Exemplo de Resposta**:

    ```json
    {
        "items": [
            {
                "id": 1,
                "price_of_sell": 250.75,
                "bar_code": "1547896589570",
                "section": "Eletrônico",
                "initial_inventory": 50,
                "expiration_date": "2024-06-15",
                "image": "garrafa.png"
            }
        ],
        "total": 1,
        "page": 1,
        "size": 50,
        "pages": 1
    }
    ```
    """

    if bar_code:
        if not re.match(r'^\d{13}$', bar_code):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
    
    if min_price_of_sell:
        if not re.match(r'^\d{1,10}(.\d{1,2})?$', str(min_price_of_sell)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if max_price_of_sell:
        if not re.match(r'^\d{1,10}(.\d{1,2})?$', str(max_price_of_sell)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if min_initial_inventory:
        if not re.match(r'^\d+$', str(min_initial_inventory)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if max_initial_inventory:
        if not re.match(r'^\d+$', str(max_initial_inventory)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if min_expiration_date:
        if not re.match(r'^(?:(?:19|20)\d{2})-(?:(?:0[1-9]|1[0-2]))-(?:(?:0[1-9]|[12]\d|3[01]))$', str(min_expiration_date)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if max_expiration_date:
        if not re.match(r'^(?:(?:19|20)\d{2})-(?:(?:0[1-9]|1[0-2]))-(?:(?:0[1-9]|[12]\d|3[01]))$', str(max_expiration_date)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
    
    verify_status(current_user)

    return paginate(products_service.get_all_products(ordering, 
                                                      section, 
                                                      bar_code, 
                                                      min_price_of_sell, 
                                                      max_price_of_sell, 
                                                      min_initial_inventory, 
                                                      max_initial_inventory, 
                                                      min_expiration_date, 
                                                      max_expiration_date))


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
async def get_product(id: int, current_user: Users = Depends(users_service.get_current_user)):

    """
    Retorna um produto.
    
    - **id**: id do produto
    - **price_of_sell**: preço de venda do produto
    - **bar_code**: código de barras do produto
    - **section**: seção do produto
    - **initial_inventory**: quantidade em estoque do produto
    - **expiration_date**: data de validade do produto
    - **image**: imagem do produto

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e o `token_type` obtidos no login para que a requisição seja realizada.
    
    **Casos de Uso**:

    - Obter um produto específico pelo seu id.

    **Exemplo de Resposta**:

    ```json
    {
        "id": 8,
        "price_of_sell": 500.55,
        "bar_code": "1234567891012",
        "section": "Vestuário",
        "initial_inventory": 50,
        "expiration_date": "2024-06-19",
        "image": "camisa_3.png"
    }
    ```
    """

    verify_status(current_user)

    return products_service.get_product_by_id(id) 


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = ProductsRead)
async def post_product(product: Products, current_user: Users = Depends(users_service.get_current_user)):

    """
    Cadastra um novo produto.
    
    - **id**: id do produto
    - **price_of_sell**: preço de venda do produto
    - **bar_code**: código de barras do produto
    - **section**: seção do produto
    - **initial_inventory**: quantidade em estoque do produto
    - **expiration_date**: data de validade do produto
    - **image**: imagem do produto

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.

    **Casos de Uso**:

    - Cadastrar um novo produto no sistema.

    **Exemplo de Requisição**:

    ```json
    {
        "price_of_sell": 500.55,
        "bar_code": "1234567891012",
        "section": "Vestuário",
        "initial_inventory": 50,
        "expiration_date": "2024-06-19",
        "image": "camisa_3.png"
    }
    ```

    **Exemplo de Resposta**:

    ```json
    {
        "id": 8,
        "price_of_sell": 500.55,
        "bar_code": "1234567891012",
        "section": "Vestuário",
        "initial_inventory": 50,
        "expiration_date": "2024-06-19",
        "image": "camisa_3.png"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return products_service.create_product(product)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
def up_product(id: int, product: ProductsUpdate, current_user: Users = Depends(users_service.get_current_user)):

    """
    Atualizar um produto.
    
    - **id**: id do produto
    - **price_of_sell**: preço de venda do produto
    - **bar_code**: código de barras do produto
    - **section**: seção do produto
    - **initial_inventory**: quantidade em estoque do produto
    - **expiration_date**: data de validade do produto
    - **image**: imagem do produto

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.
    
    **Casos de Uso**:

    - Atualizar um produto cadastrado.

    **Exemplo de Requisição**:

    ```json
    {
        "price_of_sell": 210.55
    }
    ```

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "price_of_sell": 210.55,
        "bar_code": "1547896589572",
        "section": "Eletrônico",
        "initial_inventory": 28,
        "expiration_date": "2024-06-16",
        "image": "na"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return products_service.update_product(id, product)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
def del_product(id: int, current_user: Users = Depends(users_service.get_current_user)):

    """
    Deletar um produto.
    
    - **id**: id do produto
    - **price_of_sell**: preço de venda do produto
    - **bar_code**: código de barras do produto
    - **section**: seção do produto
    - **initial_inventory**: quantidade em estoque do produto
    - **expiration_date**: data de validade do produto
    - **image**: imagem do produto

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.
  
    **Casos de Uso**:

    - Deletar um produto cadastrado.

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "price_of_sell": 210.55,
        "bar_code": "1547896589572",
        "section": "Eletrônico",
        "initial_inventory": 28,
        "expiration_date": "2024-06-16",
        "image": "na"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return products_service.delete_product(id)