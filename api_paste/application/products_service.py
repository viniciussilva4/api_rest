from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlmodel import Session, delete, select

from persistence.db_utils import get_engine
from presentation.viewmodels.models import Products, ProductsUpdate


class ProductsService:


    def __init__(self):

        self.session = Session(get_engine())


    def get_all_products(self, ordering = None):


        if not ordering:

            products = self.session.query(Products)

        else:            

            products = self.session.query(Products).order_by(*ordering)

        self.session.close()
        
        return products
    

    def count_products(self):
        
        query = select(Products)
        products = self.session.exec(query).fetchall()
        self.session.close()
        
        return len(products)
    

    def get_product_by_id(self, id: int):

        query = select(Products).where(Products.id == id)
        product = self.session.exec(query).first()
        
        if not product:

            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Produto não encontrado')

        self.session.close()

        return product

    
    def create_product(self, product: Products):

        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        self.session.close()

        return product
    

    def update_product(self, id: int, product: ProductsUpdate):

        current_product = self.get_product_by_id(id)
        
        if product.description:

            current_product.description = product.description
        
        if product.price_of_sell:
            
            current_product.price_of_sell = product.price_of_sell

        if product.bar_code:
            
            current_product.bar_code = product.bar_code

        if product.section:
            
            current_product.section = product.section

        if product.initial_inventory:
            
            current_product.initial_inventory = product.initial_inventory

        if product.expiration_date:
            
            current_product.expiration_date = product.expiration_date

        if product.image:
            
            current_product.image = product.image

        self.session.add(current_product)
        self.session.commit()
        self.session.refresh(current_product)
        self.session.close()

        return current_product
    

    def delete_product(self, id: int):

        product = self.get_product_by_id(id)
        query = delete(Products).where(Products.id == id)
        self.session.exec(query)
        self.session.commit()
        self.session.close()

        return product