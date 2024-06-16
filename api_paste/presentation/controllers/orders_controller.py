from fastapi import APIRouter, HTTPException, status

from application.orders_service import OrdersService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import *

engine = get_engine()

router = APIRouter()
prefix = '/orders'

orders_service = OrdersService()

@router.get('/', status_code = status.HTTP_200_OK, response_model = list[OrdersRead])
async def get_orders():

    return orders_service.get_all_orders()


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
async def get_client(id: int):

    order = orders_service.get_order_by_id(id)

    if not order:

        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Pedido não encontrado!') 

    return order


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = OrdersRead)
async def post_orders(order: OrdersCreate):

    return orders_service.create_order(order)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
def del_product(id: int):

    return orders_service.delete_order(id)