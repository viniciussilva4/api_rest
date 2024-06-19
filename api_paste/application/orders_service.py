from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlmodel import Session, delete, select
from contextlib import contextmanager

from persistence.db_utils import get_engine
from presentation.viewmodels.models import Orders, OrdersCreate, OrderProductLink, OrdersUpdate, Products

@contextmanager
def get_session(self):
    session = self.Session()
    try:
        yield session
    finally:
        session.close()


class OrdersService:


    def __init__(self):

        self.session = Session(get_engine())


    def get_all_orders(self, 
                       ordering = None, 
                       min_period = None, 
                       max_period = None, 
                       products_section = None, 
                       status = None, 
                       client_id = None):
        
        if not ordering:

            orders = self.session.query(Orders)

            if min_period:

                orders = orders.filter(Orders.period >= min_period)

            if max_period:

                orders = orders.filter(Orders.period <= max_period)

            if products_section:

                orders = orders.filter(Orders.products_section == products_section)

            if status:

                orders = orders.filter(Orders.status == status)

            if client_id:

                orders = orders.filter(Orders.client_id == client_id)

        else:            

            orders = self.session.query(Orders).order_by(*ordering)

            if min_period:

                orders = orders.filter(Orders.period >= min_period)

            if max_period:

                orders = orders.filter(Orders.period <= max_period)

            if products_section:

                orders = orders.filter(Orders.products_section == products_section)

            if status:

                orders = orders.filter(Orders.status == status)

            if client_id:

                orders = orders.filter(Orders.client_id == client_id)
            
        for order in orders:
            self.session.refresh(order, attribute_names = ["products"])
        self.session.close()
        
        return orders
    

    def get_order_by_id(self, id: int):
        
        query = select(Orders).where(Orders.id == id)
        order = self.session.exec(query).first()

        if not order:

            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Pedido não encontrado!')

        self.session.refresh(order, attribute_names = ["products"])
        self.session.close()

        return order
    

    def create_order(self, order: OrdersCreate):

        products_list = []

        for index in range(len(order.products)):

            query = select(Products).where(Products.id == order.products[index])
            product = self.session.exec(query).first()
        
            if not product:

                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Produto não encontrado')

            if product.initial_inventory < order.quantity[index]:

                raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f'Produto de id {product.id} insuficiente!')
            
            product.initial_inventory -= order.quantity[index]
            
            products_list.append(product)

        for product_up in products_list:

            self.session.add(product_up)

        self.session.commit()

        order_db = Orders(period = order.period, products_section = order.products_section, status = order.status, client_id = order.client)

        self.session.add(order_db)
        self.session.commit()
        self.session.refresh(order_db)

        orderproductlink_list = []

        for index in range(len(order.products)):

            orderproductlink_list.append(OrderProductLink(order_id = order_db.id, product_id = order.products[index], quantity = order.quantity[index]))

        for orderproductlink in orderproductlink_list:

            self.session.add(orderproductlink)

        self.session.commit()

        return order_db
    

    def update_order(self, id: int, order: OrdersUpdate):

        current_order = self.get_order_by_id(id)

        if order.period:
            
            current_order.period = order.period


        if order.products_section:
            
            current_order.products_section = order.products_section


        if order.status:
            
            current_order.status = order.status

        if order.client:
            
            current_order.client_id = order.client

        self.session.add(current_order)
        self.session.commit()
        self.session.refresh(current_order)
        self.session.refresh(current_order, attribute_names = ["products"])
        self.session.close()

        return current_order
    

    def delete_order(self, id: int):

        order = self.get_order_by_id(id)
        query = delete(Orders).where(Orders.id == id)
        self.session.exec(query)
        self.session.commit()
        self.session.close()

        return order