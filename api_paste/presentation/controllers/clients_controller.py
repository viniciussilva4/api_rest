from fastapi import APIRouter, status, Depends

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

@router.get('/', status_code = status.HTTP_200_OK, response_model = list[ClientsRead])
async def get_clients(current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return clients_service.get_all_clients()


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