from pydantic import BaseModel

from .household_schema import HouseholdDTO
from .user_schema import UserDTO
from typing import Optional


class ChoreBase(BaseModel):
    name: str
    description: str
    startDate: str
    intervalDays: int
    language: str


class ChoreCreate(ChoreBase):
    pass


class ChoreEdit(BaseModel):
    name: Optional[str]
    description: Optional[str]
    startDate: Optional[str]
    intervalDays: Optional[int]
    language: Optional[str]


class Chore(ChoreBase):
    id: int
    user: UserDTO
    household: HouseholdDTO
    nextOccurrence: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ChoreDTO:
    def __init__(self, id, name, description, userDto, householdDto, startDate, nextOccurence, intervalDays, language):
        self.id = id
        self.name = name
        self.description = description
        self.user = userDto
        self.household = householdDto
        self.startDate = startDate
        self.nextOccurence = nextOccurence
        self.intervalDays = intervalDays
        self.language = language
