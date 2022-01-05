from typing import List
from pydantic import BaseModel

from .user_schema import User


class ChoreBase(BaseModel):
    name: str
    description: str
    nextOccurrence: str


class ChoreCreate(ChoreBase):
    house_id: int
    user_id: int
    pass


class Chore(ChoreBase):
    id: int

    class Config:
        orm_mode = True

        # export
        # interface
        # ChoreDTO
        # {
        #     id: number;
        # name: string;
        # description: string;
        # user?: UserDTO;
        # household: HouseholdDTO;
        # nextOccurrence: string;
        # }
