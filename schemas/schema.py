from datetime import timedelta, datetime
from typing import Annotated

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.auth import UserCreate, TokenData
from config import SECRET_KEY, ALGORITHM
from db import DB

oauth2_sh = OAuth2PasswordBearer(tokenUrl="/login")


class FastAPIAuth():
    def __init__(self) -> None:
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Authentication Part
    def get_record(self, key: str, value: str) -> dict | None:
        return DB.db.userDetails.find_one({key: value}, projection={"_id": 0})

    def query_user(self, user_id: str):
        user = self.get_record('email', user_id)
        return user if user else None

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def authenticate_user(self, email, password):
        user = self.query_user(email)
        if user:
            self.pwd_context.verify(password, user['password'])
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    def create_access_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    @staticmethod
    def get_user(username: str):
        user_data = DB.db.userDetails.find_one({"email": username})
        if user_data:
            return UserCreate(**user_data)
        else:
            return {"message": "User is Not registered"}

    @staticmethod
    def get_current_user(token: Annotated[str, Depends(oauth2_sh)]):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = FastAPIAuth.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    def get_current_active_user(
        current_user: Annotated[UserCreate, Depends(
            get_current_user)]
    ):
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
