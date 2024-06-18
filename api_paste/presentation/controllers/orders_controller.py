from fastapi import APIRouter, status, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from typing import Optional

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
async def get_orders(ordering = Depends(get_ordering), current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return paginate(orders_service.get_all_orders(ordering))


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
async def get_order(id: int, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return orders_service.get_order_by_id(id)


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = OrdersRead)
async def post_orders(order: OrdersCreate, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return orders_service.create_order(order)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
def up_product(id: int, order: OrdersUpdate, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return orders_service.update_order(id, order)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
def del_order(id: int, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return orders_service.delete_order(id)