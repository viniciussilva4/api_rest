from sqlmodel import Field, SQLModel, Column, Relationship
from datetime import date
from sqlalchemy import DECIMAL, Column, ForeignKey
from sqlalchemy.orm import joinedload
from typing import Optional, List


class OrderProductLink(SQLModel, table=True):
    
    id: int = Field(default = None, primary_key = True)
    order_id: Optional[int] = Field(default = None, sa_column = Column(ForeignKey("orders.id", ondelete = "CASCADE")))
    product_id: Optional[int] = Field(default = None, sa_column = Column(ForeignKey("products.id", ondelete = "CASCADE")))
    quantity: int = Field(default = 1)

    order: "Orders" = Relationship(back_populates = "products")
    products: "Products" = Relationship(back_populates = "orders")


class ClientsBase(SQLModel):

    id: int = Field(default = None, primary_key = True)


class Clients(ClientsBase, table = True):

    id: int = Field(default = None, primary_key = True)
    cpf: str = Field(default = None, max_length = 11, unique = True, nullable = False)
    email: str = Field(default = None, unique = True, nullable = False)
    name: str = Field(default = None, max_length = 50, nullable = False)

    orders: List["Orders"] = Relationship(back_populates = "client")


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

    id: int = Field(default = None, primary_key = True)


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
        
        orm_mode = True


class OrdersCreate(OrdersBase):

    period: Optional[date] = None
    products_section: str
    status: bool
    client: int
    products: List[int]
    quantity: List[int]


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
    description: str = Field(default = 'ProductDefaultDescription')
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

    description: str
    price_of_sell: float
    bar_code: str
    section: str
    initial_inventory: int
    expiration_date: Optional[date]
    image: str


class ProductsUpdate(SQLModel):

    description: Optional[str] = None
    price_of_sell: Optional[float] = None
    bar_code: Optional[str] = None
    section: Optional[str] = None
    initial_inventory: Optional[int] = None
    expiration_date: Optional[date] = None
    image: Optional[str] = None