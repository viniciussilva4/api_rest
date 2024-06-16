from fastapi import APIRouter, HTTPException, status

from application.products_service import ProductsService
from persistence.db_utils import get_engine
from presentation.viewmodels.models import *

engine = get_engine()

router = APIRouter()
prefix = '/products'

products_service = ProductsService()

@router.get('/', status_code = status.HTTP_200_OK, response_model = list[ProductsRead])
async def get_products():

    return products_service.get_all_products()


@router.get('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
async def get_product(id: int):

    product = products_service.get_product_by_id(id)

    if not product:

        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Produto não encontrado!') 

    return product


@router.post('/', status_code = status.HTTP_201_CREATED, response_model = ProductsRead)
async def post_product(product: Products):

    return products_service.create_product(product)


@router.put('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
def up_product(id: int, product: Products):

    return products_service.update_product(id, product)


@router.delete('/{id}', status_code = status.HTTP_200_OK, response_model = ProductsRead)
def del_product(id: int):

    return products_service.delete_product(id)