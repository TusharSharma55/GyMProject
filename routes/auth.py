import logging

from datetime import timedelta
from fastapi.encoders import jsonable_encoder

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status

from db import DB
from schemas.schema import FastAPIAuth as mg
from models.auth import User, UserCreate, AccessToken
from logging_config import formater, file_handler


logger = logging.getLogger(__name__)
file_handler.setFormatter(formater)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


auth_router = APIRouter(tags=['auth'])


@auth_router.post("/signup", response_model=User, tags=["auth"])
def sign_up(user: UserCreate):
    logger.info(f"Signup attempt for email: {user.email}")

    if DB.db.userDetails.find_one(filter={"email": user.email}):
        logger.warning(f"Email already registered: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    user.password = mg().get_password_hash(user.password)
    DB.db.userDetails.insert_one(jsonable_encoder(user))

    logger.info(f"User registered successfully: {user.email}")

    return User.parse_obj(user.dict())


@auth_router.post("/login", response_model=AccessToken, tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_email = form_data.username
    password = form_data.password

    if mg().authenticate_user(user_email, password):
        logger.info(f"User {user_email} logged in")  # Log user login event
        access_token = mg().create_access_token(
            data={"sub": user_email}, expires_delta=timedelta(minutes=15)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        # Log failed login attempt
        logger.warning(f"Failed login attempt for user {user_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
