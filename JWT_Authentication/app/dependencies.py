from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from passlib.context import CryptContext
from app.database import get_session
from fastapi.security import OAuth2PasswordBearer
from app.models.user_models import User
from app.auth import verify_token
SessionDependency =Annotated[Session, Depends(get_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDependency):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user