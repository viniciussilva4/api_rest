from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlmodel import Session, delete, select
from sqlalchemy.exc import IntegrityError

from persistence.db_utils import get_engine
from presentation.viewmodels.models import Products, ProductsUpdate


class ProductsService:


    def __init__(self):

        self.session = Session(get_engine())


    def get_all_products(self, 
                         ordering = None, 
                         section = None,
                         bar_code = None, 
                         min_price_of_sell = None, 
                         max_price_of_sell = None, 
                         min_initial_inventory = None, 
                         max_initial_inventory = None, 
                         min_expiration_date = None, 
                         max_expiration_date = None):


        if not ordering:

            products = self.session.query(Products)

            if section:       

                products = products.filter(Products.section == section)

            if bar_code:       

                products = products.filter(Products.bar_code == bar_code)

            if min_price_of_sell:       

                products = products.filter(Products.price_of_sell >= min_price_of_sell)

            if max_price_of_sell:       

                products = products.filter(Products.price_of_sell <= max_price_of_sell)

            if min_initial_inventory:       

                products = products.filter(Products.initial_inventory >= min_initial_inventory)

            if max_initial_inventory:       

                products = products.filter(Products.price_of_sell <= max_initial_inventory)

            if min_expiration_date:       

                products = products.filter(Products.expiration_date >= min_expiration_date)

            if max_expiration_date:       

                products = products.filter(Products.expiration_date <= max_expiration_date)

        else:     

            products = self.session.query(Products).order_by(*ordering)

            if section:       

                products = products.filter(Products.section == section)

            if bar_code:       

                products = products.filter(Products.bar_code == bar_code)

            if min_price_of_sell:       

                products = products.filter(Products.price_of_sell >= min_price_of_sell)

            if max_price_of_sell:       

                products = products.filter(Products.price_of_sell <= max_price_of_sell)

            if min_initial_inventory:       

                products = products.filter(Products.initial_inventory >= min_initial_inventory)

            if max_initial_inventory:       

                products = products.filter(Products.price_of_sell <= max_initial_inventory)

            if min_expiration_date:       

                products = products.filter(Products.expiration_date >= min_expiration_date)

            if max_expiration_date:       

                products = products.filter(Products.expiration_date <= max_expiration_date)

        self.session.close()
        
        return products
    

    def get_product_by_id(self, id: int):

        query = select(Products).where(Products.id == id)
        product = self.session.exec(query).first()
        
        if not product:

            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = 'Produto não encontrado')

        self.session.close()

        return product

    
    def create_product(self, product: Products):

        try:

            self.session.add(product)
            self.session.commit()
            self.session.refresh(product)
            self.session.close()

            return product
        
        except IntegrityError:

            self.session.rollback()

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Código de barras já cadastrado ou erro na requisição!')
    

    def update_product(self, id: int, product: ProductsUpdate):

        current_product = self.get_product_by_id(id)
        
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