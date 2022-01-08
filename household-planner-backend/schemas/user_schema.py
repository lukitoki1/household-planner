from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    # phone_number: str

class UserUpdate(BaseModel):
    name: Optional[str] = None

class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserDTO:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
