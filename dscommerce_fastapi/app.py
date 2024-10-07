from http import HTTPStatus

from fastapi import FastAPI

from dscommerce_fastapi.routers import auth, users
from dscommerce_fastapi.schemas import Message

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)


# response model é o Model de resposta, ou seja,
# o formato da classe de resposta
@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello World!'}
