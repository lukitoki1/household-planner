from typing import List
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    phone_number: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    households: List[BaseModel] = []

    class Config:
        orm_mode = True
