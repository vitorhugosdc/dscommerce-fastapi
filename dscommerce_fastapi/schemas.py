# aqui contém tudo relacionado a modelo/contrato de entrada e saida de dados,
# não tem nada a ver com a representação dos Models no banco
from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


# é o tipo de dado que representa o usuário, sendo também o tipo de dado que
# sera recebido no POST, ou seja, é um modelo de contrato de ENTRADA
class UserSchema(BaseModel):
    name: str
    username: str
    email: EmailStr
    phone: str
    password: str


# UserDB hearda de UserSchema, ou seja, contém todos os campos de UserSchema
# + id, basicamente serve para representar um usuário no banco de dados que
# possui um id agora
# class UserDB(UserSchema):
#    id: int


# é o mesmo conceito de um DTO, utilizado para não retornar a senha na resposta
# ou seja, é um modelo de contrato de SAÍDA, inclusive contendo o novo id dele
class UserPublic(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    phone: str
    # Significa que é pra validar os objetos pelos ATRIBUTOS
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
