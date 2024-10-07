from sqlalchemy import select
from sqlalchemy.orm import Session

from dscommerce_fastapi.db.models.users import User


# Session é a sessão recebida direto da fixture no conftest.py
def test_create_user_db(session: Session):
    user = User(
        name='John Doe',
        username='johndoe',
        email='johndoe@me.com',
        phone='123456789',
        password='secret',
    )

    session.add(user)
    session.commit()
    # session.refresh(user)

    result = session.scalar(select(User).where(User.email == 'johndoe@me.com'))

    assert result.username == 'johndoe'
