from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from typing import Optional
import re

from application.clients_service import ClientsService
from application.users_service import UsersService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import Clients, ClientsRead, ClientsUpdate
from presentation.viewmodels.models import Users
from security.validators import verify_role, verify_status

engine = get_engine()

router = APIRouter()
prefix = '/clients'

clients_service = ClientsService()
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

                order_params.append(asc(getattr(Clients, atributes[index].strip())))

            else:

                order_params.append(desc(getattr(Clients, atributes[index].strip())))

    except AttributeError:

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Requisição mal realizada!')

    return order_params


@router.get('/', status_code = status.HTTP_200_OK, response_model = Page[ClientsRead])
async def get_clients(current_user: Users = Depends(users_service.get_current_user), 
                      ordering = Depends(get_ordering), 
                      cpf: Optional[str] = Query(None), 
                      email: Optional[str] = Query(None), 
                      name: Optional[str] = Query(None)):
    
    """
    Retorna uma pagina com uma lista de todos os clientes.
    
    - **items**: lista de produtos
    - **id**: id do cliente
    - **cpf**: cpf do cliente
    - **email**: email do cliente
    - **name**: nome do cliente

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
    - O `cpf` deve ser uma sequência de caracteres(string), do cpf que se deseja filtrar. 
    É opcional, mas se preenchido deve ter 13 caracteres de números
    - O `email` deve ser uma sequência de caracteres(string), do email que se deseja filtrar. 
    É opcional, mas se preenchido deve ser uma sequência de caracteres seguida de um arroba, uma sequência de caracteres, um ponto e uma sequência de caracteres.
    - O `name` deve ser uma sequência de caracteres(string), do nome que se deseja filtrar.
    É opcional, deve ser uma sequência de caracteres de no máximo 50 valores, incluindo espaços.

    **Casos de Uso**:

    - Listar todos os clientes.

    **Exemplo de Resposta**:

    ```json
    {
        "items": [
            {
                "id": 1,
                "email": "jorge@gmail.com",
                "cpf": "12345678910",
                "name": "Jorge Matheus"
            }
        ],
        "total": 1,
        "page": 1,
        "size": 50,
        "pages": 1
    }
    ```
    """

    if cpf:
        if not re.match(r'^\d{11}$', cpf):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
    
    if email:
        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if name:
        if not re.match(r'^[A-Za-zÀ-ÿ\s]{1,50}$', name):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")

    verify_status(current_user)

    return paginate(clients_service.get_all_clients(ordering, cpf, email, name))


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
async def get_client(id: int, current_user: Users = Depends(users_service.get_current_user)):

    """
    Retorna um cliente.
    
    - **id**: id do cliente
    - **cpf**: cpf do cliente
    - **email**: email do cliente
    - **name**: nome do cliente

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e o `token_type` obtidos no login para que a requisição seja realizada.

    **Casos de Uso**:

    - Obter um cliente específico pelo seu id.

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "email": "jorge@gmail.com",
        "cpf": "12345678910",
        "name": "Jorge Matheus"
    }
    ```
    """

    verify_status(current_user)

    return clients_service.get_client_by_id(id)


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = ClientsRead)
async def post_client(client: Clients, current_user: Users = Depends(users_service.get_current_user)):

    """
    Cadastra um novo cliente.
    
    - **id**: id do cliente
    - **cpf**: cpf do cliente
    - **email**: email do cliente
    - **name**: nome do cliente

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.

    **Casos de Uso**:

    - Cadastrar um novo cliente no sistema.

    **Exemplo de Requisição**:

    ```json
    {
        "email": "jorge@gmail.com",
        "cpf": "12345678910",
        "name": "Jorge Matheus"
    }
    ```

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "email": "jorge@gmail.com",
        "cpf": "12345678910",
        "name": "Jorge Matheus"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return clients_service.create_client(client)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
def up_client(id: int, client: ClientsUpdate, current_user: Users = Depends(users_service.get_current_user)):

    """
    Atualizar um cliente.
    
    - **id**: id do cliente
    - **cpf**: cpf do cliente
    - **email**: email do cliente
    - **name**: nome do cliente

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.
      
    **Casos de Uso**:

    - Atualizar um cliente cadastrado.

    **Exemplo de Requisição**:

    ```json
    {
        "cpf": "15478965232"
    }
    ```

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "email": "marcelo_araujo@gmail.com",
        "cpf": "15478965232",
        "name": "Marcelo Sena Araujo"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return clients_service.update_client(id, client)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
def del_client(id: int, current_user: Users = Depends(users_service.get_current_user)):

    """
    Deletar um cliente.
    
    - **id**: id do cliente
    - **cpf**: cpf do cliente
    - **email**: email do cliente
    - **name**: nome do cliente

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.
  
    **Casos de Uso**:

    - Deletar um cliente cadastrado.

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "email": "marcelo_araujo@gmail.com",
        "cpf": "15478965232",
        "name": "Marcelo Sena Araujo"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return clients_service.delete_client(id)