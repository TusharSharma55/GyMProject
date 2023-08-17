from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr = "johndoe@mail.com"
    is_active: bool = True
    name: str = "John Doe"


class UserUpdate(BaseModel):
    name: str = "John Doe"
    is_active: bool = True
    password: str = "secret"


class UserCreate(UserBase):
    password: str = "secret"


class User(UserBase):
    pass


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
