from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from dscommerce_fastapi.database import get_session
from dscommerce_fastapi.db.models.users import User
from dscommerce_fastapi.schemas import (
    Message,
    UserPublic,
    UserSchema,
)
from dscommerce_fastapi.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated['Session', Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(data: UserSchema, db: T_Session):
    query = select(User).where(
        (User.username == data.username) | (User.email == data.email)
    )
    db_user = db.scalar(query)

    if db_user:
        if db_user.username == data.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        # acho que não precisa do elif, somente if
        elif db_user.email == data.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(data.password)

    db_user = User(
        name=data.name,
        username=data.username,
        email=data.email,
        phone=data.phone,
        password=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get('', status_code=HTTPStatus.OK, response_model=list[UserPublic])
def read_users(
    db: T_Session,
    current_user: T_CurrentUser,
    limit: int = 10,
    offset: int = 0,
):
    query = select(User).limit(limit).offset(offset)
    users = db.scalars(query).all()
    return users


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def put_user(
    user_id: int,
    data: UserSchema,
    db: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    current_user.name = data.name
    current_user.username = data.username
    current_user.email = data.email
    current_user.phone = data.phone

    db.commit()
    db.refresh(current_user)

    return current_user


@router.get('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def get_user(user_id: int, db: T_Session, current_user: T_CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    return current_user


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(user_id: int, db: T_Session, current_user: T_CurrentUser):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    current_user.is_active = False
    db.commit()
    db.refresh(current_user)

    return {'message': 'User deleted successfully'}
