from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from db.database import Base
from models.household_members import household_members


class User(Base):
    __tablename__ = "users"

    id = Column("user_id", Integer, primary_key=True, index=True)
    name = Column("user_name", String)
    email = Column("user_email", String)
    phone_number = Column("user_phone_numeber", Numeric)
    households = relationship(
        "Household",
        secondary=household_members,
        back_populates="users")
