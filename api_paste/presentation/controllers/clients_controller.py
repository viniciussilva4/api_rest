from fastapi import APIRouter, HTTPException, status
from typing import Annotated
from fastapi import Depends

from application.clients_service import ClientsService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import Clients, ClientsRead, ClientsUpdate

engine = get_engine()

router = APIRouter()
prefix = '/clients'

clients_service = ClientsService()

@router.get('/', status_code = status.HTTP_200_OK, response_model = list[ClientsRead])
async def get_clients():

    return clients_service.get_all_clients()


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
async def get_client(id: int):

    return clients_service.get_client_by_id(id)


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = ClientsRead)
async def post_client(client: Clients):

    return clients_service.create_client(client)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
def up_client(id: int, client: ClientsUpdate):

    return clients_service.update_client(id, client)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = ClientsRead)
def del_client(id: int):

    return clients_service.delete_client(id)