from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlmodel import Session, delete, select
from sqlalchemy.orm import joinedload

from persistence.db_utils import get_engine
from presentation.viewmodels.models import Orders, OrdersCreate, OrderProductLink
from .products_service import ProductsService


products_service = ProductsService()


class OrdersService:


    def __init__(self):

        self.session = Session(get_engine())


    def get_all_orders(self):
        
        query = select(Orders)
        orders = self.session.exec(query).fetchall()
        for order in orders:
            self.session.refresh(order, attribute_names = ["products"])
        self.session.close()
        return orders
    

    def get_order_by_id(self, id: int):
        
        query = select(Orders).where(Orders.id == id)
        order = self.session.exec(query).first()
        self.session.refresh(order, attribute_names = ["products"])
        self.session.close()

        return order
    

    def create_order(self, order: OrdersCreate):

        try:

            order_database = Orders(period = order.period, products_section = order.products_section, status = order.status, client = order.client)
            self.session.add(order_database)
            self.session.commit()
            self.session.refresh(order_database)

            for products, quantity in zip(order.products, order.quantity):

                product = products_service.get_product_by_id(products)

                if not product:

                    self.session.rollback()

                    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Produto de id {products} não encontrado!')
                
                if product.initial_inventory < quantity:

                    self.session.rollback()

                    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f'Produto de id {products} insuficiente!')
                
                product.initial_inventory -= quantity
                self.session.add(product)
                order_product_link = OrderProductLink(order_id = order_database.id, product_id = product.id, quantity = quantity)
                self.session.add(order_product_link)

            self.session.commit()

        finally:

            self.session.refresh(order_database, attribute_names = ["products"])

            order_database = order_database

            self.session.close()

            return order_database
    

    def delete_order(self, id: int):

        order = self.get_order_by_id(id)
    
        if not order:

            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Produto não encontrado!')
        
        query = delete(Orders).where(Orders.id == id)
        self.session.exec(query)
        self.session.commit()
        self.session.refresh(order, attribute_names = ["products"])
        self.session.close()

        return order