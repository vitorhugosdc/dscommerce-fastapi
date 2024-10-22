from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from dscommerce_fastapi.database import get_session
from dscommerce_fastapi.db.models.orders import Order
from dscommerce_fastapi.db.models.products import Product
from dscommerce_fastapi.db.models.users import User
from dscommerce_fastapi.schemas import Message
from dscommerce_fastapi.security import get_current_user

router = APIRouter(prefix='/orders', tags=['orders'])

T_Session = Annotated['Session', Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


class OrderCreate(BaseModel):
    products_ids: list[int]


class UserRead(BaseModel):
    id: int
    name: str


class ProductRead(BaseModel):
    id: int
    name: str


class PaymentRead(BaseModel):
    id: int
    moment: datetime


class OrderRead(BaseModel):
    id: int
    status: Order.OrderStatus
    created_at: datetime
    client: UserRead
    products: list[ProductRead]
    payment: PaymentRead | None


@router.post('', status_code=HTTPStatus.CREATED, response_model=OrderRead)
def create_order(
    session: T_Session, current_user: T_CurrentUser, data: OrderCreate
):
    query = select(Product).where(
        Product.id.in_(data.products_ids), Product.is_active
    )
    products = session.scalars(query).all()

    # se o número for diferente, significa que algum produto não existe ou nao está ativo
    if len(products) != len(data.products_ids):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Product not found'
        )

    db_order = Order(
        client=current_user, status=Order.OrderStatus.WAITING_PAYMENT
    )

    db_order.products = products

    session.add(db_order)
    session.commit()

    return db_order


@router.get('', status_code=HTTPStatus.OK, response_model=list[OrderRead])
def read_orders(
    session: T_Session,
    current_user: T_CurrentUser,
    limit: int = 10,
    offset: int = 0,
):
    query = (
        select(Order)
        .options(
            joinedload(Order.client),
            joinedload(Order.payment),
            selectinload(Order.products),
        )
        .where(Order.client_id == current_user.id)
        .limit(limit)
        .offset(offset)
    )

    orders = session.scalars(query).all()

    return orders


@router.get('/{order_id}', status_code=HTTPStatus.OK, response_model=OrderRead)
def get_order(order_id: int, session: T_Session, current_user: T_CurrentUser):
    query = (
        select(Order)
        .options(
            joinedload(Order.client),
            joinedload(Order.payment),
            selectinload(Order.products),
        )
        .where(Order.id == order_id, Order.client_id == current_user.id)
    )

    order = session.scalar(query)

    if not order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Order not found'
        )

    return order
