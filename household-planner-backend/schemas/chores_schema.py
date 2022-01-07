from pydantic import BaseModel

from .household_schema import HouseholdDTO
from .user_schema import UserDTO


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
    user: UserDTO
    household: HouseholdDTO

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
