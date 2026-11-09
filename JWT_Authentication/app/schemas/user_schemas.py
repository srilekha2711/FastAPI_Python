from sqlmodel import SQLModel


class CreateUser(SQLModel):
    name:str
    email:str
    password:str

class LoginUser(SQLModel):
    email:str
    password:str

class Token(SQLModel):
    access_token: str
    token_type: str