from datetime import timedelta
from fastapi.encoders import jsonable_encoder

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status

from db import DB
from schemas.schema import FastAPIAuth as mg
from models.auth import User, UserCreate, AccessToken


auth_router = APIRouter(tags=['auth'])


@auth_router.post("/signup", response_model=User, tags=["auth"])
def sign_up(user: UserCreate):
    if DB.db.userDetails.find_one(filter={"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    user.password = mg().get_password_hash(user.password)
    DB.db.userDetails.insert_one(jsonable_encoder(user))
    return {"message": f"created user {user.email!r}"}


@auth_router.post("/login", response_model=AccessToken, tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_email = form_data.username
    password = form_data.password

    if mg().authenticate_user(user_email, password):
        access_token = mg().create_access_token(
            data={"sub": user_email}, expires_delta=timedelta(minutes=15)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
