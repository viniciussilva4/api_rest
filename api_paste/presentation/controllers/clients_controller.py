from fastapi import APIRouter, status, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from typing import Optional

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
async def get_clients(ordering = Depends(get_ordering), current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return paginate(clients_service.get_all_clients(ordering))


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
async def get_client(id: int, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return clients_service.get_client_by_id(id)


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = ClientsRead)
async def post_client(client: Clients, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return clients_service.create_client(client)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
def up_client(id: int, client: ClientsUpdate, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return clients_service.update_client(id, client)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
def del_client(id: int, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return clients_service.delete_client(id)