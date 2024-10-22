from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI

from dscommerce_fastapi.db import create_user
from dscommerce_fastapi.routers import (
    auth,
    categories,
    orders,
    payments,
    products,
    users,
)
from dscommerce_fastapi.schemas import Message


@asynccontextmanager
async def lifespan(app: FastAPI):
    # before the app starts
    create_user()
    yield
    # after the app ends


app = FastAPI(lifespan=lifespan)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(orders.router)
app.include_router(payments.router)


# response model é o Model de resposta, ou seja,
# o formato da classe de resposta
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}
