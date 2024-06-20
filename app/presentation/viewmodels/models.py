from sqlmodel import Field, SQLModel, Column, Relationship
from datetime import date
from sqlalchemy import DECIMAL, Column, ForeignKey, asc, desc
from sqlalchemy.orm import validates
from typing import Optional, List
from enum import Enum
from fastapi import HTTPException, status
import re


class Token(SQLModel):

    access_token: str
    token_type: str


class LoginData(SQLModel):

    login: Optional[str] = None
    password: Optional[str] = None


class UsersRole(str, Enum):

    manager = "manager"
    functionary = "functionary"


class UsersBase(SQLModel):

    name: str = Field(default = None, max_length = 50, nullable = False)


class Users(UsersBase, table = True):

    id: int = Field(default = None, primary_key = True)
    name: str = Field(default = None, max_length = 50, nullable = False)
    login: str = Field(default = None, max_length = 50, nullable = False)
    password: str = Field(default = None, nullable = False)
    status: bool = Field(default = True)
    role: UsersRole  = Field(default = "functionary", nullable = False)


class UsersRead(UsersBase):

    name: str 
    status: bool
    role: UsersRole


class UsersReadId(UsersBase):

    id: int
    name: str 
    status: bool
    role: UsersRole


class UsersCreate(UsersBase):

    name: str
    login: str
    password: str
    status: bool = True
    role: UsersRole


class UsersUpdate(UsersBase):

    name: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    status: Optional[bool] = None
    role: Optional[UsersRole] = None


class OrderProductLink(SQLModel, table = True):
    
    id: int = Field(default = None, primary_key = True)
    order_id: Optional[int] = Field(default = None, sa_column = Column(ForeignKey("orders.id", ondelete = "CASCADE")))
    product_id: Optional[int] = Field(default = None, sa_column = Column(ForeignKey("products.id", ondelete = "CASCADE")))
    quantity: int = Field(default = 1)

    order: "Orders" = Relationship(back_populates = "products")
    products: "Products" = Relationship(back_populates = "orders")


class ClientsBase(SQLModel):

    name: str = Field(default = None, max_length = 50, nullable = False)


class Clients(ClientsBase, table = True):

    id: int = Field(default = None, primary_key = True)
    cpf: str = Field(default = None, max_length = 11, unique = True, nullable = False)
    email: str = Field(default = None, unique = True, nullable = False)
    name: str = Field(default = None, max_length = 50, nullable = False)

    orders: List["Orders"] = Relationship(back_populates = "client")

    @validates('cpf')
    def validate_cpf(self, key, cpf):

        
        if not re.match(r'^\d{11}$', cpf):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "CPF com formatação errada!")
        
        return cpf

    @validates('email')
    def validate_email(self, key, email):

        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Email com formatação errada!")

        return email
    
    @validates('name')
    def validate_email(self, key, name):

        if not re.match(r'^[A-ZÁÉÍÓÚÄËÏÖÜÀÈÌÒÙÂÊÎÔÛÇÑ][a-záéíóúäëïöüàèìòùâêîôûçñA-ZÁÉÍÓÚÄËÏÖÜÀÈÌÒÙÂÊÎÔÛÇÑ\s]{9,49}$', name):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Nome com formatação errada!")
        
        if len(name.replace(" ", "")) < 10:

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Nome com formatação errada!")

        return name


class ClientsRead(ClientsBase):

    id: int
    email: str 
    cpf: str
    name: str 


class ClientsUpdate(SQLModel):

    cpf: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None


class OrdersBase(SQLModel):

    products_section: str = Field(default = 'ProductDefaultSection')


class Orders(OrdersBase, table = True):

    period: Optional[date] = Field(default = None)
    id: int = Field(default = None, primary_key = True)
    products_section: str = Field(default = 'ProductDefaultSection')
    status: bool = Field(default = False)
    client_id: int = Field(default = None, foreign_key = "clients.id")
    products: List[OrderProductLink] = Relationship(back_populates = "order")

    client: "Clients" = Relationship(back_populates = "orders")


class OrdersRead(OrdersBase):

    id: int
    period: Optional[date]
    products_section: str
    status: bool
    client_id: int
    products: List[OrderProductLink]


    class Config:
        
        from_attributes = True


class OrdersCreate(OrdersBase):

    period: Optional[date]
    products_section: str
    status: bool
    client: int
    products: List[int]
    quantity: List[int]

    @validates('period')
    def validate_period(self, key, period):

        if not re.match(r'^(?:(?:19|20)\d{2})-(?:(?:0[1-9]|1[0-2]))-(?:(?:0[1-9]|[12]\d|3[01]))$', str(period)):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Data com formatação errada!")

        return period
    
    @validates('status')
    def validate_status(self, key, status):

        if not re.match(r'^(?i)(true|false)$', status):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Status com formatação errada!")

        return status
    
    @validates('client_id')
    def validate_id(self, key, client_id):

        if not re.match(r'^(0|[1-9]\d*)$', client_id):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "ID do cliente com formatação errada!")

        return client_id


class OrdersUpdate(SQLModel):

    period: Optional[date] = None
    products_section: Optional[str] = None
    status: Optional[bool] = None
    client: Optional[int] = None
    products: Optional[int] = None
    quantity:  Optional[int] = None


class ProductsBase(SQLModel):
    
    id: int = Field(default = None, primary_key = True)


class Products(ProductsBase, table = True):

    id: int = Field(default = None, primary_key = True)
    price_of_sell: float = Field(default = 0.00, sa_column = Column(DECIMAL(10, 2)))
    bar_code: str = Field(default = '0000000000000', max_length = 13, unique = True, nullable = False)
    section: str = Field(default = 'ProductDefaultSection')
    initial_inventory: int = Field(default = 1)
    expiration_date: Optional[date] = Field(default = None)
    image: str

    orders: List[OrderProductLink] = Relationship(back_populates = "products")

    class Config:

        arbitrary_types_allowed = True
        

class ProductsRead(ProductsBase):


    id: int
    price_of_sell: float
    bar_code: str
    section: str
    initial_inventory: int
    expiration_date: Optional[date]
    image: str


class ProductsUpdate(SQLModel):

    price_of_sell: Optional[float] = None
    bar_code: Optional[str] = None
    section: Optional[str] = None
    initial_inventory: Optional[int] = None
    expiration_date: Optional[date] = None
    image: Optional[str] = None

    @validates('price_of_sell')
    def validate_email(self, key, price_of_sell):

        if not re.match(r'^\d{1,10}(.\d{1,2})?$', price_of_sell):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Preço de venda com formatação errada!")

        return price_of_sell
    
    @validates('bar_code')
    def validate_email(self, key, bar_code):

        if not re.match(r'^\d{13}$', bar_code):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Código de barras com formatação errada!")

        return bar_code
    
    @validates('initial_inventory')
    def validate_email(self, key, initial_inventory):

        if not re.match(r'^\d+$', initial_inventory):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Estoque com formatação errada!")

        return initial_inventory
    
    @validates('expiration_date')
    def validate_email(self, key, expiration_date):

        if not re.match(r'^(?:(?:19|20)\d{2})-(?:(?:0[1-9]|1[0-2]))-(?:(?:0[1-9]|[12]\d|3[01]))$', expiration_date):

            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Data de validade com formatação errada!")

        return expiration_date