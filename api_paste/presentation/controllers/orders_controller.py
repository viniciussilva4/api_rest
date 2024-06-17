from fastapi import APIRouter, HTTPException, status

from application.orders_service import OrdersService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import OrdersRead, OrdersUpdate, OrdersCreate

engine = get_engine()

router = APIRouter()
prefix = '/orders'

orders_service = OrdersService()

@router.get('/', status_code = status.HTTP_200_OK, response_model = list[OrdersRead])
async def get_orders():

    return orders_service.get_all_orders()


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
async def get_order(id: int):

    return orders_service.get_order_by_id(id)


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = OrdersRead)
async def post_orders(order: OrdersCreate):

    return orders_service.create_order(order)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
def up_product(id: int, order: OrdersUpdate):

    return orders_service.update_order(id, order)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = OrdersRead)
def del_order(id: int):

    return orders_service.delete_order(id)