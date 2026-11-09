from fastapi import Depends, HTTPException,UploadFile, HTTPException, APIRouter
from fastapi.concurrency import asynccontextmanager
from sqlmodel import select
from typing import Annotated
from app.dependencies import SessionDependency, get_current_user
from app.schemas.user_schemas import CreateUser, Token, LoginUser
from app.models.user_models import User
from app.auth import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post('/register')
def register(session: SessionDependency, user_data: CreateUser):
    if session.exec(select(User).where(User.email == user_data.email)).first():
        raise HTTPException(status_code=400, detail = "Email is already registered")
    hash_pwd = hash_password(user_data.password)

    user = User(email =user_data.email, name = user_data.name, hashed_password=hash_pwd)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post('/login', response_model=Token)
def login(session: SessionDependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    pwd =verify_password(form_data.password, user.hashed_password)

    if not user or not pwd:
        raise HTTPException(status_code=401, detail = "Invalid email or password")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get('/profile')
def profile(current_user: Annotated[User, Depends(get_current_user)]):
    return {"name": current_user.name, "email": current_user.email}