from fastapi import APIRouter, status, Depends

from application.auth_service import UsersService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import Token, LoginData, Users, UsersRead, UsersCreate
from security.validators import verify_role, verify_status


engine = get_engine()

router = APIRouter()
prefix = '/users'

users_service = UsersService()


@router.post('/login', status_code = status.HTTP_200_OK, response_model = Token)
async def get_token(login_data: LoginData = Depends()):

    return users_service.generate_token(login_data)


@router.post('/{id}', status_code = status.HTTP_200_OK, response_model = UsersRead)
async def get_user(id: int, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return users_service.get_user_by_id(id) 


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = UsersRead)
async def create_user(user: UsersCreate, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return users_service.create_user(user)