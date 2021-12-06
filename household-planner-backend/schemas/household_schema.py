from typing import List
from pydantic import BaseModel

from .user_schema import User


class HouseholdBase(BaseModel):
    name: str


class HouseholdCreate(HouseholdBase):
    pass


class Household(HouseholdBase):
    id: int
    users: List[User] = []

    class Config:
        orm_mode = True
