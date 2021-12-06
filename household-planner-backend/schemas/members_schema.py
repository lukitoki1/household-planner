from typing import List
from pydantic import BaseModel

class MemberBase(BaseModel):
    house_id: int


class MemberCreate(MemberBase):
    email: str


class Member(MemberBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True