from fastapi import APIRouter, status, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc
from typing import Optional

from application.products_service import ProductsService
from application.users_service import UsersService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import Products, ProductsRead, ProductsUpdate
from presentation.viewmodels.models import Users
from security.validators import verify_role, verify_status

engine = get_engine()

router = APIRouter()
prefix = '/products'

products_service = ProductsService()
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

                order_params.append(asc(getattr(Products, atributes[index].strip())))

            else:

                order_params.append(desc(getattr(Products, atributes[index].strip())))

    except AttributeError:

        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Requisição mal realizada!')

    return order_params


@router.get('/', status_code = status.HTTP_200_OK, response_model = Page[ProductsRead])
async def get_products(ordering = Depends(get_ordering), current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return paginate(products_service.get_all_products(ordering))


@router.get('/count', status_code = status.HTTP_200_OK, response_model = int)
async def get_products_count(current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return products_service.count_products()


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
async def get_product(id: int, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)

    return products_service.get_product_by_id(id) 


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = ProductsRead)
async def post_product(product: Products, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return products_service.create_product(product)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
def up_product(id: int, product: ProductsUpdate, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return products_service.update_product(id, product)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
def del_product(id: int, current_user: Users = Depends(users_service.get_current_user)):

    verify_status(current_user)
    verify_role(current_user)

    return products_service.delete_product(id)