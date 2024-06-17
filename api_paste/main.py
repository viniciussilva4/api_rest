from fastapi import FastAPI
from sqlmodel import SQLModel

from presentation.controllers.clients_controller import router as clients_router, prefix as clients_prefix
from presentation.controllers.orders_controller import router as orders_router, prefix as orders_prefix
from presentation.controllers.products_controller import router as products_router, prefix as products_prefix
from presentation.controllers.auth_controller import router as auth_router, prefix as auth_prefix
from persistence.db_utils import get_engine

app = FastAPI()

engine = get_engine()
SQLModel.metadata.create_all(engine)

app.include_router(clients_router, prefix = clients_prefix)
app.include_router(orders_router, prefix = orders_prefix)
app.include_router(products_router, prefix = products_prefix)
app.include_router(auth_router, prefix = auth_prefix)