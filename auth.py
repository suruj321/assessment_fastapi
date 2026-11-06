# import os
# import secrets
# from dotenv import load_dotenv
# from fastapi import HTTPException, Header
# load_dotenv()
# api_key = os.getenv("API_KEY")
# print(api_key)

# def verify_api_key(x_Api_key:str=Header()):
#     if not secrets.compare_digest(x_Api_key, api_key):
#         raise HTTPException(status_code=401, detail="invalid api key")
#     return x_Api_key



from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from database import get_session
from models import User

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(status_code=401,detail="Invalid or expired token")
    statement = select(User).where(User.id == int(user_id))
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=401,detail="User not found")
    return user
