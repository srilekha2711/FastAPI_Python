from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends, Form,File, HTTPException,UploadFile, HTTPException, UploadFile
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Annotated
from models import User, CreateUser

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



UPLOADS_DIRS ="uploads"
os.makedirs(UPLOADS_DIRS, exist_ok= True)

@app.post('/createuser')
def usercreate(
    session: SessionDependency,
    name:str =Form(...),
    phone:int= Form(...),
    email:str =Form(),
    file:UploadFile=File(...)
):
    user_data = {'name': name, 'phone': phone, 'email': email}
    validated = CreateUser.model_validate(user_data)

    file_path = os.path.join(UPLOADS_DIRS, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    user = User(**validated.model_dump(),file_path=f"{UPLOADS_DIRS}/{file.filename}")
    session.add(user)
    session.commit()    
    session.refresh(user)
    return user

@app.post('/create')
def create_user(user: CreateUser, session: SessionDependency):
    new_user=User.model_validate(user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.get('/users', response_model=list[User])
def get_users(session: SessionDependency):
    users=session.exec(select(User)).all()
    if not users:
        raise HTTPException(status_code=404, detail ="No users found")
    return users

@app.get('/users/{user_id}', response_model=User)
def get_single_user(user_id:int,session: SessionDependency):
    user=session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail ="User not found")
    return user

@app.put('/users/{user_id}', response_model=User)
def update_user(user_id:int, update: CreateUser, session: SessionDependency):
    user=session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail ="User not found")
    user.name=update.name
    user.phone=update.phone
    user.email=update.email
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.delete('/users/{user_id}')
def delete_user(user_id:int, session: SessionDependency):
    user=session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail ="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}