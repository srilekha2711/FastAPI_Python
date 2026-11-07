from fastapi import FastAPI,Depends, Form,File, HTTPException,UploadFile, HTTPException, UploadFile
from fastapi.concurrency import asynccontextmanager
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Annotated
from models import User, CreateUser, LoginUser
from passlib.context import CryptContext

import os, shutil

DATABASE_URL = "sqlite:///./users.db"
engine=create_engine(DATABASE_URL, echo=True)

@asynccontextmanager
async def lifeSpan(ap: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifeSpan)
def get_session():
    with Session(engine) as session:
        yield session
SessionDependency =Annotated[Session, Depends(get_session)]

#Auth

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated="auto")

def hash_password(password: str) ->str:
    print("Password received:", repr(password))
    print("Password length:", len(password))
    print("Password bytes:", len(password.encode("utf-8")))
    return pwd_context.hash(password)

def verify_password(plain:str, hashed:str) -> bool:
    return pwd_context.verify(plain, hashed)

@app.post('/register')
def register(session: SessionDependency, user_data: CreateUser):
    if session.exec(select(User).where(User.email == user_data.email)).first():
        raise HTTPException(status_code=400, detail = "Email is already registered")
    hash_pwd = hash_password(user_data.password)

    user = User(email =user_data.email, name = user_data.name, hashed_password=hash_pwd)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post('/login')
def login(session: SessionDependency, login_user:LoginUser):
    user = session.exec(select(User).where(User.email ==login_user.email)).first()

    pwd =verify_password(login_user.password, user.hashed_password)

    if not user or not pwd:
        raise HTTPException(status_code=401, detail = "Invalid email or password")
    return user