from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from dscommerce_fastapi.database import get_session
from dscommerce_fastapi.db.models.products import Product
from dscommerce_fastapi.db.models.users import User
from dscommerce_fastapi.security import get_current_user

router = APIRouter(prefix='/products', tags=['products'])

T_Session = Annotated['Session', Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


# receber
class ProductCreate(BaseModel):
    name: str
    serial_code: str
    description: str | None = None
    price: float
    img_url: str


# retornar
class ProductRead(BaseModel):
    id: int
    name: str
    serial_code: str
    description: str | None = None
    price: float
    img_url: str

    model_config = ConfigDict(from_attributes=True)


class ListProductRead(BaseModel):
    products: list[ProductRead]


@router.post('', status_code=HTTPStatus.CREATED, response_model=ProductRead)
def create_product(data: ProductCreate, db: T_Session):
    query = select(Product).where(Product.serial_code == data.serial_code)
    db_product = db.scalar(query)
    if db_product:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Product already exists'
        )

    # precisava do exclude description sendo que já tem o unset?
    db_product = Product(**data.model_dump(exclude_unset=True))

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get('', status_code=HTTPStatus.OK, response_model=ListProductRead)
def read_products(
    db: T_Session,
    limit: int = 10,
    offset: int = 0,
):
    query = select(Product).limit(limit).offset(offset)
    db_products = db.scalars(query).all()

    return {'products': db_products}
