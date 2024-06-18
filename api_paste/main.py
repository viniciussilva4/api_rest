from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi_pagination import add_pagination

from presentation.controllers.clients_controller import router as clients_router, prefix as clients_prefix
from presentation.controllers.orders_controller import router as orders_router, prefix as orders_prefix
from presentation.controllers.products_controller import router as products_router, prefix as products_prefix
from presentation.controllers.users_controller import router as users_router, prefix as users_prefix
from persistence.db_utils import get_engine

app = FastAPI()
add_pagination(app)

engine = get_engine()
SQLModel.metadata.create_all(engine)

app.include_router(clients_router, prefix = clients_prefix)
app.include_router(orders_router, prefix = orders_prefix)
app.include_router(products_router, prefix = products_prefix)
app.include_router(users_router, prefix = users_prefix)