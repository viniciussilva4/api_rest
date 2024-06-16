from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlmodel import Session, delete, select
from sqlalchemy.orm import joinedload

from persistence.db_utils import get_engine
from presentation.viewmodels.models import Orders, OrdersCreate, OrderProductLink, OrdersUpdate
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

        if not order:

            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Pedido não encontrado!')

        self.session.refresh(order, attribute_names = ["products"])
        self.session.close()

        return order
    

    def create_order(self, order: OrdersCreate):

        products_list = []

        for index in range(len(order.products)):

            product = products_service.get_product_by_id(order.products[index])

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

        self.session.close()

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