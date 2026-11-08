from fastapi import FastAPI,Depends, Form,File, HTTPException,UploadFile, HTTPException, UploadFile
from fastapi.concurrency import asynccontextmanager
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Annotated
from models import User, CreateUser, LoginUser, Token
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

DATABASE_URL = "sqlite:///./users.db"
engine=create_engine(DATABASE_URL, echo=True)

@asynccontextmanager
async def lifeSpan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifeSpan)
def get_session():
    with Session(engine) as session:
        yield session
SessionDependency =Annotated[Session, Depends(get_session)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "mysecretKey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token( data: dict, expires_delta: timedelta | None =None):
    to_encode = data.copy()
    expire =datetime.now(timezone.utc) + (expires_delta or timedelta(minutes =15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except  JWTError:
        return None

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDependency):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


    


#Auth

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated="auto")

def hash_password(password: str) ->str:
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

@app.post('/login', response_model=Token)
def login(session: SessionDependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    pwd =verify_password(form_data.password, user.hashed_password)

    if not user or not pwd:
        raise HTTPException(status_code=401, detail = "Invalid email or password")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.get('/profile')
def profile(current_user: Annotated[User, Depends(get_current_user)]):
    return {"name": current_user.name, "email": current_user.email}