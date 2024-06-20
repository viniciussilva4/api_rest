from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from typing import Optional
from datetime import date
import re

from application.orders_service import OrdersService
from application.users_service import UsersService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import Orders, OrdersRead, OrdersUpdate, OrdersCreate
from presentation.viewmodels.models import Users
from security.validators import verify_role, verify_status

engine = get_engine()

router = APIRouter()
prefix = '/orders'

orders_service = OrdersService()
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

                order_params.append(asc(getattr(Orders, atributes[index].strip())))

            else:

                order_params.append(desc(getattr(Orders, atributes[index].strip())))

    except AttributeError:

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Requisição mal realizada!')

    return order_params


@router.get('/', status_code = status.HTTP_200_OK, response_model = Page[OrdersRead])
async def get_orders(current_user: Users = Depends(users_service.get_current_user), 
                     ordering = Depends(get_ordering),
                     min_period: Optional[date] = Query(None),
                     max_period: Optional[date] = Query(None),
                     products_section: Optional[str] = Query(None),
                     status: Optional[bool] = Query(None),
                     client_id: Optional[int] = Query(None)):
    
    """
    Retorna uma pagina com uma lista de todos os pedidos.
    
    - **items**: lista de pedidos
    - **id**: id do pedido
    - **period**: data do pedido
    - **products_section**: seção de produtos do pedido
    - **status**: situação do pedido
    - **client_id**: id do cliente do pedido
    - **products**: lista dos produtos

    - **id**: id do da relação do pedido e do produto
    - **order_id**: id do pedido
    - **product_id**: id do produto
    - **quantity**: quantidade do produto

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
    - O `min_period` deve ser uma sequência de caracteres(string), da menor data do pedido.
    É opcional, mas se preenchido deve estar no formato AAAA-MM-DD como 2024-06-20, por exemplo.
    - O `max_period` deve ser uma sequência de caracteres(string), da maior data do pedido.
    É opcional, mas se preenchido deve estar no formato AAAA-MM-DD como 2024-06-20, por exemplo.
    - O `products_section` deve ser uma sequência de caracteres(string), da seção dos produtos que se deseja filtrar. 
    É opcional.
    - O `status` deve ser uma sequência de caractere(string), do estado do pedido que se deseja filtrar.
    É opcional, mas se preenchido deve ser `true` ou 'false'.
    - O `client_id` deve ser uma sequência de caractere(string), do id do cliente que se deseja filtrar.
    É opcional, mas se preenchido deve ser um número inteiro positivo.

    **Casos de Uso**:

    - Listar todos os pedidos.

    **Exemplo de Resposta**:

    ```json
    {
        "items": [
            {
                "id": 1,
                "period": "2024-06-16",
                "products_section": "Eletrônico",
                "status": false,
                "client_id": 1,
                "products": [
                    {
                        "id": 1,
                        "order_id": 1,
                        "product_id": 1,
                        "quantity": 5
                    },
                    {
                        "id": 2,
                        "order_id": 1,
                        "product_id": 2,
                        "quantity": 5
                    }
                ]
        }
    ],
        "total": 1,
        "page": 1,
        "size": 50,
        "pages": 1
    }
    ```
    """
    
    if min_period:
        if not re.match(r'^(?:(?:19|20)\d{2})-(?:(?:0[1-9]|1[0-2]))-(?:(?:0[1-9]|[12]\d|3[01]))$', str(min_period)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
    
    if max_period:
        if not re.match(r'^(?:(?:19|20)\d{2})-(?:(?:0[1-9]|1[0-2]))-(?:(?:0[1-9]|[12]\d|3[01]))$', str(max_period)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if status:
        if not re.match(r'^(?i)(true|false)$', str(status)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if client_id:
        if not re.match(r'^(0|[1-9]\d*)$', str(client_id)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")

    verify_status(current_user)

    return paginate(orders_service.get_all_orders(ordering, min_period, max_period, products_section, status, client_id))


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
async def get_order(id: int, current_user: Users = Depends(users_service.get_current_user)):

    """
    Retorna um pedido.
    
    - **id**: id do pedido
    - **period**: data do pedido
    - **products_section**: seção de produtos do pedido
    - **status**: situação do pedido
    - **client_id**: id do cliente do pedido
    - **products**: lista dos produtos

    - **id**: id do da relação do pedido e do produto
    - **order_id**: id do pedido
    - **product_id**: id do produto
    - **quantity**: quantidade do produto

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e o `token_type` obtidos no login para que a requisição seja realizada.

    **Casos de Uso**:

    - Obter um pedido específico pelo seu id.

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "period": "2024-06-16",
        "products_section": "Eletrônico",
        "status": false,
        "client_id": 1,
        "products": [
            {
                "id": 1,
                "order_id": 1,
                "product_id": 1,
                "quantity": 5
            },
            {
                "id": 2,
                "order_id": 1,
                "product_id": 2,
                "quantity": 5
            }
        ]
    }
    ```
    """

    verify_status(current_user)

    return orders_service.get_order_by_id(id)


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = OrdersRead)
async def post_orders(order: OrdersCreate, current_user: Users = Depends(users_service.get_current_user)):

    """
    Cadastra um novo pedido.
    
    - **id**: id do pedido
    - **period**: data do pedido
    - **products_section**: seção de produtos do pedido
    - **status**: situação do pedido
    - **client_id**: id do cliente do pedido
    - **products**: lista dos produtos

    - **id**: id do da relação do pedido e do produto
    - **order_id**: id do pedido
    - **product_id**: id do produto
    - **quantity**: quantidade do produto

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.

    **Casos de Uso**:

    - Cadastrar um novo pedido no sistema.

    **Exemplo de Requisição**:

    ```json
    {
        "period": "2024-06-19",
        "products_section": "Vestuário",
        "status": true,
        "client": 1,
        "products": [
            4
        ],
        "quantity": [
            20
        ]
    }
    ```

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "period": "2024-06-19",
        "products_section": "Vestuário",
        "status": true,
        "client_id": 1,
        "products": [
            {
                "id": 15,
                "order_id": 10,
                "product_id": 4,
                "quantity": 20
            }
        ]
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    if not re.match(r'^(?:(?:19|20)\d{2})-(?:(?:0[1-9]|1[0-2]))-(?:(?:0[1-9]|[12]\d|3[01]))$', str(order.period)):

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Data com formatação errada!")

    if not re.match(r'^(?i:true|false)$', str(order.status)):

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Status com formatação errada!")

    if not re.match(r'^(0|[1-9]\d*)$', str(order.client)):

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "ID do cliente com formatação errada!")

    return orders_service.create_order(order)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
def up_order(id: int, order: OrdersUpdate, current_user: Users = Depends(users_service.get_current_user)):

    """
    Atualizar um pedido.
    
    - **id**: id do pedido
    - **period**: data do pedido
    - **products_section**: seção de produtos do pedido
    - **status**: situação do pedido
    - **client_id**: id do cliente do pedido
    - **products**: lista dos produtos

    - **id**: id do da relação do pedido e do produto
    - **order_id**: id do pedido
    - **product_id**: id do produto
    - **quantity**: quantidade do produto

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.
    
    **Casos de Uso**:

    - Atualizar um pedido cadastrado.

    **Exemplo de Requisição**:

    ```json
    {
        "period": "2024-06-19"
    }
    ```

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "period": "2024-06-19",
        "products_section": "Eletrônico",
        "status": false,
        "client_id": 1,
        "products": [
            {
                "id": 1,
                "order_id": 1,
                "product_id": 1,
                "quantity": 5
            },
            {
                "id": 2,
                "order_id": 1,
                "product_id": 2,
                "quantity": 5
            }
        ]
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return orders_service.update_order(id, order)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
def del_order(id: int, current_user: Users = Depends(users_service.get_current_user)):

    """
    Deletar um pedido.
    
    - **id**: id do pedido
    - **period**: data do pedido
    - **products_section**: seção de produtos do pedido
    - **status**: situação do pedido
    - **client_id**: id do cliente do pedido
    - **products**: lista dos produtos

    - **id**: id do da relação do pedido e do produto
    - **order_id**: id do pedido
    - **product_id**: id do produto
    - **quantity**: quantidade do produto

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.
    
    **Casos de Uso**:

    - Deletar um pedido cadastrado.

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "period": "2024-06-19",
        "products_section": "Vestuário",
        "status": true,
        "client_id": 1,
        "products": [
            {
                "id": 15,
                "order_id": 10,
                "product_id": 4,
                "quantity": 20
            }
        ]
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return orders_service.delete_order(id)