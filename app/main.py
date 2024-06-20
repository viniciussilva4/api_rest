from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel
from fastapi_pagination import add_pagination
import rollbar
from rollbar.contrib.fastapi import add_to as rollbar_add_to
from rollbar.contrib.fastapi import ReporterMiddleware as RollbarMiddleware
from dotenv import load_dotenv
import os

from presentation.controllers.clients_controller import router as clients_router, prefix as clients_prefix
from presentation.controllers.orders_controller import router as orders_router, prefix as orders_prefix
from presentation.controllers.products_controller import router as products_router, prefix as products_prefix
from presentation.controllers.users_controller import router as users_router, prefix as users_prefix
from persistence.db_utils import get_engine

load_dotenv()

ROLLBAR_TOKEN = os.getenv('ROLLBAR_TOKEN')


rollbar.init(ROLLBAR_TOKEN, environment = 'development', handler = 'async')

app = FastAPI()
add_pagination(app)
app.add_middleware(RollbarMiddleware)

#@app.exception_handler(RequestValidationError)

#async def validation_exception_handler(request: Request, exc: RequestValidationError):

    #raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Erro na requisição')

engine = get_engine()
SQLModel.metadata.create_all(engine)

app.include_router(clients_router, prefix = clients_prefix)
app.include_router(orders_router, prefix = orders_prefix)
app.include_router(products_router, prefix = products_prefix)
app.include_router(users_router, prefix = users_prefix)