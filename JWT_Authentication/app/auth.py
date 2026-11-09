
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

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




    


#Auth

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated="auto")

def hash_password(password: str) ->str:
    return pwd_context.hash(password)

def verify_password(plain:str, hashed:str) -> bool:
    return pwd_context.verify(plain, hashed)

