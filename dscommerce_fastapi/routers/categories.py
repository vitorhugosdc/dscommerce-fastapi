from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from dscommerce_fastapi.database import get_session
from dscommerce_fastapi.db.models.categories import Category
from dscommerce_fastapi.db.models.products import Product
from dscommerce_fastapi.db.models.users import User
from dscommerce_fastapi.schemas import Message
from dscommerce_fastapi.security import get_current_user

router = APIRouter(prefix='/categories', tags=['categories'])

T_Session = Annotated['Session', Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


class CategoryCreate(BaseModel):
    name: str


class CategoryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ListCategoryRead(BaseModel):
    categories: list[CategoryRead]


@router.post('', status_code=HTTPStatus.CREATED, response_model=CategoryRead)
def create_category(
    data: CategoryCreate, db: T_Session, current_user: T_CurrentUser
):
    db_category = Category(
        created_by=current_user, **data.model_dump(exclude_unset=True)
    )

    # o nome é unique, mas no model já tem que a verificação é feita no DB
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get('', status_code=HTTPStatus.OK, response_model=ListCategoryRead)
def read_categories(
    db: T_Session, name: str | None = None, limit=10, offset=0
):
    query = (
        select(Category).limit(limit).offset(offset).where(Category.is_active)
    )

    if name:
        # contais é o %LIKE%
        query = query.filter(Category.name.contains(name))
        # apenas uma maneira de fazer oq foi feito no name acima,
        # poderia ser f'{name}%' ou f'%{name}' também
        # query = query.filter(Category.name.like(f'%{name}%'))
        # query = query.where(Category.name.like(f'%{name}%'))
    db_categories = db.scalars(query).all()

    return {'categories': db_categories}


class CategoryUpdate(BaseModel):
    name: str | None = None


@router.patch(
    '/{category_id}', status_code=HTTPStatus.OK, response_model=CategoryRead
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: T_Session,
    current_user: T_CurrentUser,
):
    query = select(Category).where(
        Category.id == category_id, Category.is_active
    )
    db_category = db.scalar(query)
    if not db_category:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Category not found'
        )

    # if current_user.id != db_category.created_by:
    #     raise HTTPException(
    #         status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
    #     )

    # se fosse vários atributos poderia ser assim
    # for key, value in data.model_dump(exclude_unset=True).items():
    #     setattr(db_category, key, value)

    # mas como tem um atributo só, pode ser assim:

    if data.name:
        db_category.name = data.name

    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get(
    '/{category_id}', status_code=HTTPStatus.OK, response_model=CategoryRead
)
def get_category(category_id: int, db: T_Session, current_user: T_CurrentUser):
    query = select(Category).where(
        Category.id == category_id, Category.is_active
    )

    db_category = db.scalar(query)

    if not db_category:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Category not found'
        )

    return db_category


# Como o produto deve ter uma categoria, devemos fazer alguma coisa pra
# categoria deletada não aparecer lá em products, ou seja, remover da tabela de associação
@router.delete(
    '/{category_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_category(
    category_id: int, db: T_Session, current_user: T_CurrentUser
):
    query = select(Category).where(
        Category.id == category_id, Category.is_active
    )

    db_category = db.scalar(query)

    if not db_category:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Category not found'
        )

    # if current_user.id != db_category.created_by:
    #     raise HTTPException(
    #         status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
    #     )

    # query = (
    #     select(Product)
    #     .join(Product.categories)
    #     .options(selectinload(Product.categories))
    #     .where(Product.categories.any(id=db_category.id))
    # )

    # db_products = db.scalars(query).all()

    # for product in db_products:
    #     product.categories.remove(db_category)

    db_category.is_active = False
    db_category.deleted_at = datetime.now(UTC)
    # poderia ser só o id?
    # db_category.deleted_by_id = current_user.id
    db_category.deleted_by = current_user
    # db.delete(db_category)
    db.commit()
    return {'message': 'Category deleted successfully'}
