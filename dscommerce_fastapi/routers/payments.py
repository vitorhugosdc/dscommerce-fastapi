from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from dscommerce_fastapi.database import get_session
from dscommerce_fastapi.db.models.orders import Order
from dscommerce_fastapi.db.models.payment import Payment
from dscommerce_fastapi.db.models.users import User
from dscommerce_fastapi.schemas import Message
from dscommerce_fastapi.security import get_current_user

router = APIRouter(prefix='/payments', tags=['payments'])

T_Session = Annotated['Session', Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


class PaymentCreate(BaseModel):
    order_id: int


# @router.post('/{order_id}', status_code=HTTPStatus.CREATED, response_model=Message)
# def create_payment(
#     order_id: int, session: T_Session, current_user: T_CurrentUser, data: PaymentCreate
# ):
@router.post('', status_code=HTTPStatus.CREATED, response_model=Message)
def create_payment(
    session: T_Session, current_user: T_CurrentUser, data: PaymentCreate
):
    query = select(Order).where(
        Order.id == data.order_id, Order.client_id == current_user.id
    )
    order = session.scalars(query).one_or_none()

    if not order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Order not found'
        )
    # aqui ele tá associando o Payment ao objeto Order que também já está monitorado pelo ORM,
    #  então não precisa fazer order.payment = Payment(order=order)
    payment = Payment(order=order)
    order.status = Order.OrderStatus.PAID
    session.add(payment)
    session.commit()

    return {'message': 'Payment created successfully'}


class UserRead(BaseModel):
    id: int
    name: str


class OrderRead(BaseModel):
    id: int
    status: Order.OrderStatus
    created_at: datetime
    # client: UserRead


class PaymentRead(BaseModel):
    id: int
    moment: datetime
    order: OrderRead
    # o client está em Order, mas vou colocar aqui pra ter 1 nível só de JSON,
    # então tenho que montar a resposta do JSON na mão ao invés dele já saber fazer se fosse em OrderRead
    client: UserRead


@router.get(
    '/{payment_id}', status_code=HTTPStatus.OK, response_model=PaymentRead
)
def get_payment(
    payment_id: int, session: T_Session, current_user: T_CurrentUser
):
    query = (
        select(Payment)
        .join(Payment.order)
        # poderia ser assim também que o sqlalchemy já saberia, mas acho que o de cima fica mais visual do que está acontecendo
        # .join(Order)
        .options(joinedload(Payment.order).options(joinedload(Order.client)))
        .where(
            Payment.id == payment_id,
            Order.client_id == current_user.id,
        )
    )
    payment = session.scalars(query).one_or_none()

    if not payment:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Payment not found'
        )

    # se client tivesse em OrderRead, era só retornar payment (return payment)
    # pois estaria aninhado certo, mas como quero que client esteja no mesmo nível de Order, tem que montar a resposta manual

    response = PaymentRead(
        id=payment.id,
        moment=payment.moment,
        order=OrderRead(
            id=payment.order.id,
            status=payment.order.status,
            created_at=payment.order.created_at,
        ),
        client=UserRead(
            id=payment.order.client.id, name=payment.order.client.name
        ),
    )
    return response


@router.get('', status_code=HTTPStatus.OK, response_model=list[PaymentRead])
def read_payments(session: T_Session, current_user: T_CurrentUser):
    query = (
        select(Payment)
        .join(Payment.order)
        .options(joinedload(Payment.order).options(joinedload(Order.client)))
        .where(Order.client_id == current_user.id)
    )

    payments = session.scalars(query).all()

    response = [
        PaymentRead(
            id=payment.id,
            moment=payment.moment,
            order=OrderRead(
                id=payment.order.id,
                status=payment.order.status,
                created_at=payment.order.created_at,
            ),
            client=UserRead(
                id=payment.order.client.id, name=payment.order.client.name
            ),
        )
        for payment in payments
    ]

    return response
