from sqlmodel import Field, SQLModel, Column, Relationship, Integer
from datetime import date
from sqlalchemy import DECIMAL, Column, ForeignKey
from typing import Optional, List


class OrderProductLink(SQLModel, table=True):
    
    id: int = Field(default = None, primary_key = True)
    order_id: Optional[int] = Field(default = None)
    product_id: Optional[int] = Field(default = None)
    quantity: int = Field(default = 1)

    #order: Optional["Orders"] = Relationship(back_populates = "products", foreign_key = "OrderProductLink.order_id")
    #product: Optional["Products"] = Relationship(back_populates = "orders", foreign_key = "OrderProductLink.product_id")

    #__tablename__ = "order_product_link"
    #__table_args__ = {"extend_existing": True}

    #order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    #product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))


class ClientsBase(SQLModel):

    name: str = Field(default = 'UserDefaultName', max_length = 50)


class Clients(ClientsBase, table = True):

    id: int = Field(default = None, primary_key = True)
    email: str = Field(default = 'userdefaultemail@email.com')
    cpf: str = Field(default='00000000000', max_length = 11)


class ClientsRead(ClientsBase):

    name: str 
    email: str 
    cpf: str


class OrdersBase(SQLModel):

    period: Optional[date] = Field(default = None)


class Orders(OrdersBase, table = True):

    id: int = Field(default = None, primary_key = True)
    products_section: str = Field(default = 'ProductDefaultSection')
    status: bool = Field(default = False)
    client: int = Field(default = None, foreign_key = "clients.id")
    products: List[OrderProductLink] = Relationship(back_populates = "order")


class OrdersRead(OrdersBase):

    id: int 
    products_section: str
    status: bool
    client: int
    products: List[OrderProductLink]


class OrdersCreate(OrdersBase):

    period: Optional[date] = None
    products_section: str
    status: bool
    client: int
    products: List[int]
    quantity: List[int]


class ProductsBase(SQLModel):
    
    description: str = Field(default = 'ProductDefaultDescription')


class Products(ProductsBase, table = True):

    id: int = Field(default = None, primary_key = True)
    price_of_sell: float = Field(default = 000.00, sa_column = Column(DECIMAL(10, 2)))
    bar_code: str = Field(default = '0000000000000', max_length = 13)
    section: str = Field(default = 'ProductDefaultSection')
    initial_inventory: int = Field(default = 0)
    expiration_date: Optional[date] = Field(default = None)
    orders: List[OrderProductLink] = Relationship(back_populates = "product")
    image: str


    class Config:

        arbitrary_types_allowed = True


class ProductsRead(ProductsBase):

    price_of_sell: float
    bar_code: str
    section: str
    initial_inventory: int
    expiration_date: date
    image: str