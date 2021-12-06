from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.database import Base
from .household_members import Members


class Household(Base):
    __tablename__ = "households"

    id = Column("hous_id", Integer, primary_key=True, index=True)
    name = Column("hous_name", String)
    users = relationship(
        "User",
        secondary=Members.__tablename__,
        back_populates="households")

    chores = relationship("Chore", back_populates="household")
