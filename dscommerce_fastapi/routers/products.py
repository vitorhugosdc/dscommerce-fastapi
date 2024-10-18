from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from dscommerce_fastapi.database import get_session
from dscommerce_fastapi.db.models.categories import Category
from dscommerce_fastapi.db.models.products import Product
from dscommerce_fastapi.db.models.users import User
from dscommerce_fastapi.schemas import Message
from dscommerce_fastapi.security import get_current_user

router = APIRouter(prefix='/products', tags=['products'])

T_Session = Annotated['Session', Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


# receber
class ProductCreate(BaseModel):
    name: str
    serial_code: str
    # str | None significaria que pode ser str ou None, mas tem que receber um deles
    # str | None = None significa que tem que ser str ou, se se não receber nada, ele automaticamente fica None
    description: str | None = None
    price: float
    img_url: str

    # daria pra fazer outro endpoint que recebe a categoria
    # como se fosse objeto mesmo, ou seja, id e nome, igual Category Read
    categories_ids: List[int]


class CategoryRead(BaseModel):
    id: int
    name: str

    # acho que não precisa, testar depois
    model_config = ConfigDict(from_attributes=True)


# retornar
class ProductRead(BaseModel):
    id: int
    name: str
    serial_code: str
    description: str | None = None
    price: float
    img_url: str
    categories: List[CategoryRead]

    model_config = ConfigDict(from_attributes=True)


@router.post('', status_code=HTTPStatus.CREATED, response_model=ProductRead)
def create_product(
    data: ProductCreate, db: T_Session, current_user: T_CurrentUser
):
    query = select(Product).where(Product.serial_code == data.serial_code)

    db_product = db.scalar(query)

    if db_product:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Product already exists'
        )

    db_product = Product(
        # por que do exclude_unset? pois se tiver algum atributo
        # que seja | None ou | None = None, ele ignora,
        # e geralmente se no recebimento pode ser 1 desses 2, é porque no banco é um campo opcional (Optional), então o proprio banco atribui Nulo/None a esse campo
        # Agora, caso precisemos tratar um atributo especifico, como no caso abaixo, precisamos garantir que as categorias existem antes de inserir no banco,
        # excluimos dela do model dump, ou seja, não vai ser setada em Products ainda, e, logo mais abaixo usamos o append pra adicionar as categorias ao Products
        **data.model_dump(exclude_unset=True, exclude={'categories_ids'})
    )
    db_product.created_by = current_user

    for category_id in data.categories_ids:
        c = db.scalar(
            select(Category).where(
                Category.id == category_id, Category.is_active
            )
        )
        if not c:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Category not found'
            )
        db_product.categories.append(c)

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.get('', status_code=HTTPStatus.OK, response_model=list[ProductRead])
def read_products(  # noqa#
    db: T_Session,
    # ao invés de vários parametros poderia fazer igual arbo
    # onde recebe uma classe com os parametros opcionais
    name: str | None = None,
    serial_code: str | None = None,
    price: float | None = None,
    description: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    # só de category estar no formato certo no ProductRead,
    # basta o join que ele retorne tudo certinho
    query = (
        select(Product)
        .options(selectinload(Product.categories))
        .limit(limit)
        .offset(offset)
        .where(Product.is_active)
    )

    if name:
        query = query.where(Product.name.contains(name))

    if serial_code:
        query = query.filter(Product.serial_code.contains(serial_code))

    if price:
        query = query.where(Product.price == price)

    if description:
        # poderia ser f'{description}%' ou f'%{description}' também poderia ser
        # query = query.filter(Product.description.like(f'%{description}%'))
        query = query.where(Product.description.like(f'%{description}%'))

    db_products = db.scalars(query).all()

    return db_products


class ProductUpdate(BaseModel):
    name: str | None = None
    serial_code: str | None = None
    description: str | None = None
    price: float | None = None
    img_url: str | None = None
    categories_ids: List[int] | None = None


@router.patch(
    '/{product_id}', status_code=HTTPStatus.OK, response_model=ProductRead
)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: T_Session,
    current_user: T_CurrentUser,
):
    query = (
        select(Product)
        .options(selectinload(Product.categories))
        .where(
            Product.id == product_id,
            Product.is_active,
            Product.created_by_id == current_user.id,
        )
    )

    db_product = db.scalar(query)

    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )

    # ------------tem que pensar dps no caso em que ele REMOVE uma categoria
    if data.categories_ids:
        # se não tivesse o selectinload lá em cima aqui estaria pesquisando
        # cada categoria em uma query separada
        categories_ids_already_in_product = [
            c.id for c in db_product.categories
        ]
        categories_ids_not_already_in_product = [
            id
            for id in data.categories_ids
            if id not in categories_ids_already_in_product
        ]

        # ---uma solução pro problema de caso alguma categoria não existem mais
        # é verificar ela no db com a flag is_active
        if categories_ids_not_already_in_product:
            query = select(Category).where(
                Category.id.in_(categories_ids_not_already_in_product)
            )

            categories = db.scalars(query).all()
            if categories:
                db_product.categories.extend(categories)

        # Maneira antiga que pensei, mas geraria várias querys pesquisando cada categoria,
        # então fiz da maneira acima que já busca tudo de uma vez
        # categories_ids = [c.id for c in db_product.categories]
        # for category_id in data.categories_ids:
        #     # caso id já não esteja associado ao produto, ou seja, categoria nova atribuida
        #     if category_id not in categories_ids:
        #         category = db.scalar(
        #             select(Category).where(Category.id == category_id)
        #         )
        #         if not category:
        #             raise HTTPException(
        #                 status_code=HTTPStatus.NOT_FOUND,
        #                 detail=f'Category with id {category_id} not found',
        #             )

    for key, value in data.model_dump(
        exclude_unset=True, exclude={'categories_ids'}
    ).items():
        setattr(db_product, key, value)

    db_product.updated_by = current_user

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.delete(
    '/{product_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_product(
    product_id: int, db: T_Session, current_user: T_CurrentUser
):
    query = select(Product).where(
        Product.id == product_id,
        Product.is_active,
        Product.created_by_id == current_user.id,
    )

    db_product = db.scalar(query)

    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )

    db_product.is_active = False
    db.commit()

    return {'message': 'Product deleted successfully'}


@router.get(
    '/{product_id}', status_code=HTTPStatus.OK, response_model=ProductRead
)
def get_product(product_id: int, db: T_Session, current_user: T_CurrentUser):
    query = (
        select(Product)
        .options(joinedload(Product.categories))
        .where(
            Product.id == product_id,
            Product.is_active,
        )
    )

    db_product = db.scalar(query)

    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Product not found'
        )

    return db_product
