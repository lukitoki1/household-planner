from typing import List
from pydantic import BaseModel


class HouseholdBase(BaseModel):
    pass


class HouseholdCreate(HouseholdBase):
    pass


class Household(HouseholdBase):
    id: int
    house_id: int
    user_id: int

    class Config:
        orm_mode = True
