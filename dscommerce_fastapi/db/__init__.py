from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from dscommerce_fastapi.settings import Settings

engine = create_engine(Settings().DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


def create_user():
    from dscommerce_fastapi.db.models.users import User

    query = select(User).where(
        User.username == '1', User.email == '1@example.com'
    )

    with SessionLocal() as session:
        user = session.scalar(query)
        if not user:
            user = User(
                name='1',
                username='1',
                email='1@example.com',
                phone='123456789',
                password='1',
            )
            session.add(user)
            session.commit()
            session.refresh(user)
