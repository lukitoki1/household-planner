from typing import List
from pydantic import BaseModel


class MemberBase(BaseModel):
    house_id: int
    is_owner: int


class MemberCreate(MemberBase):
    email: str


class Member(MemberBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class MemberDTO:
    def __init__(self, id, name, email, is_owner):
        self.id = id
        self.name = name
        self.email = email
        self.is_owner = is_owner
