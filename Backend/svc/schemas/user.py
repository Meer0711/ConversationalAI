from typing import List
from pydantic import BaseModel, EmailStr


class SignUp(BaseModel):
    account_name: str
    email: EmailStr


class SignIn(BaseModel):
    email: EmailStr
    password: str


class CreateUser(BaseModel):
    email: EmailStr


class AddBotsToUser(BaseModel):
    user_id: int
    bot_ids: List[int]
