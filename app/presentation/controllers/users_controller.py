from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi_pagination import Page
from typing import Optional
from fastapi_pagination.ext.sqlalchemy import paginate
import re
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY_USER = os.getenv('SECRET_KEY_USER')

from application.users_service import UsersService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import Token, LoginData, Users, UsersRead, UsersCreate, UsersUpdate, UsersRole, UsersReadId
from security.validators import verify_role, verify_status
from security.token_provider import create_access_token, SECRET_KEY, ALGORITHM


engine = get_engine()

router = APIRouter()
prefix = '/users'

users_service = UsersService()


@router.post('/login', status_code = status.HTTP_200_OK, response_model = Token)
async def login(login_data: LoginData = Depends()):

    """
    Retorna um token de acesso.
    - **access_token**: token de acesso
    - **token_type**: tipo do token

    **Regras de Negócio**:
    - Deve ser enviado login e senha para receber o token.

    **Casos de Uso**:

    - Realiza login.

    **Exemplo de Resposta**:

    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2dpbiI6ImpvcmdlIiwic3RhdHVzIjp0cnVlLCJyb2xlIjoibWFuYWdlciIsImV4cCI6MTcxODgyMTgyOX0.6Mklce7YOUlVCuYCB4JKQp41zEUkbPmquWPb76DIfpE",
        "token_type": "Bearer"
    }
    ```
    """

    return users_service.generate_token(login_data)


@router.get('/get_credentials', status_code = status.HTTP_200_OK, response_model = UsersRead)
async def get_credentials(current_user: Users = Depends(users_service.get_current_user), token: Optional[str] = Depends):

    """
    Retorna os dados do usuário.
    - **name**: nome do usuário
    - **status**: status do usuário
    - **role**: cargo do usuário

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido, e o `token_type` obtidos no login para que a requisição seja realizada.

    - Usado para acessar os próprios dados.

    **Exemplo de Resposta**:

    ```json
    {
        "id": 1,
        "name": "sergio",
        "status": true,
        "role": "functionary"
    }
    ```
    """
    
    verify_status(current_user)

    payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
    login: str = payload.get("login")

    return users_service.get_user_by_login(login)


@router.get('/', status_code = status.HTTP_200_OK, response_model = Page[UsersReadId])
async def get_users(current_user: Users = Depends(users_service.get_current_user), 
                    name: Optional[str] = Query(None), 
                    status: Optional[bool] = Query(None),
                    role: Optional[UsersRole] = Query(None)):
    
    """
    Retorna uma pagina com uma lista de todos os usuários.
    
    - **items**: lista de usuários
    - **id**: id do usuário
    - **name**: nome do usuário
    - **status**: status do usuário
    - **role**: cargo do usuário

    - **total**: total de itens
    - **page**: pagina atual da requisição
    - **size**: quantidade de itens por página
    - **pages**: quantidade de páginas

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.

    - *Filtros:*
    - O `name` deve ser uma sequência de caracteres(string), do nome que se deseja filtrar. 
    É opcional.
    - O `status` deve ser uma sequência de caractere(string), do estado do pedido que se deseja filtrar.
    É opcional, mas se preenchido deve ser `true` ou 'false'.
    - O `role` deve ser uma sequência de caracteres(string), do cargo que se deseja filtrar.
    É opcional, mas se preenchido deve ser 'functionary' ou 'manager'.

    **Casos de Uso**:

    - Listar todos os Usuários.

    **Exemplo de Resposta**:

    ```json
    {
        "items": [
            {
                "id": 1,
                "name": "sergio",
                "status": true,
                "role": "functionary"
            }
        ],
        "total": 1,
        "page": 1,
        "size": 50,
        "pages": 1
    }
    ```
    """
    
    verify_status(current_user)
    verify_role(current_user)

    if name:
        if not re.match(r'^[A-Za-zÀ-ÿ\s]{1,50}$', name):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")
        
    if status:
        if not re.match(r'^(?i)(true|false)$', str(status)):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Requisição mal feita!")

    return paginate(users_service.get_all_users(name, status, role))


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = UsersRead)
async def get_user(id: int, current_user: Users = Depends(users_service.get_current_user)):

    """
    Retorna um usuário.
    
    - **name**: nome do usuário
    - **status**: status do usuário
    - **role**: cargo do usuário

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e o `token_type` obtidos no login para que a requisição seja realizada.
    
    **Casos de Uso**:

    - Obter um usuário específico pelo seu id.

    **Exemplo de Resposta**:

    ```json
    {
        "name": "Sergio",
        "status": true,
        "role": "functionary"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return users_service.get_user_by_id(id) 


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = UsersRead)
async def post_user(user: UsersCreate, current_user: Users = Depends(users_service.get_current_user)):

    """
    Cadastra um novo usuário.
    
    - **name**: nome do usuário
    - **status**: status do usuário
    - **role**: cargo do usuário

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.

    **Casos de Uso**:

    - Cadastrar um novo usuário no sistema.

    **Exemplo de Requisição**:

    ```json
    {
        "name": "Sergio",
        "status": true,
        "role": "functionary"
    }
    ```

    **Exemplo de Resposta**:

    ```json
    {
        "name": "Sergio",
        "status": true,
        "role": "functionary"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return users_service.create_user(user)

@router.put('/{id}', status_code = status.HTTP_201_CREATED, response_model = UsersRead)
async def put_user(id: int, user: UsersUpdate, current_user: Users = Depends(users_service.get_current_user)):

    """
    Atualizar um usuário.
    
    - **name**: nome do usuário
    - **status**: status do usuário
    - **role**: cargo do usuário

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.
    
    **Casos de Uso**:

    - Atualizar um usuário cadastrado.

    **Exemplo de Requisição**:

    ```json
    {
        "name": Sergio
    }
    ```

    **Exemplo de Resposta**:

    ```json
    {
        "name": "Sergio",
        "status": true,
        "role": "functionary"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return users_service.update_user(id, user)

@router.delete('/{id}', status_code = status.HTTP_201_CREATED, response_model = UsersRead)
async def del_user(id: int, current_user: Users = Depends(users_service.get_current_user)):

    """
    Deletar um usuário.
    
    - **name**: nome do usuário
    - **status**: status do usuário
    - **role**: cargo do usuário

    **Regras de Negócio**:

    - *Autenticação:*
    - Na requisição deve ser enviado um `access_token` válido e de um usuário gerente, com a role `manager`, e o `token_type` obtidos no login para que a requisição seja realizada.
  
    **Casos de Uso**:

    - Deletar um usuário cadastrado.

    **Exemplo de Resposta**:

    ```json
    {
        "name": "Sergio",
        "status": true,
        "role": "functionary"
    }
    ```
    """

    verify_status(current_user)
    verify_role(current_user)

    return users_service.delete_user(id)


@router.post('/firstuser', status_code = status.HTTP_201_CREATED, response_model = UsersRead)
async def first_user(user: UsersCreate, secret_key: str):

    if secret_key == SECRET_KEY_USER:

        return users_service.create_user(user)
    
    else:

        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Chave errada!')
    
