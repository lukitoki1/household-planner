from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from db.database import Base
from .household_members import Household_member


class User(Base):
    __tablename__ = "users"

    id = Column("user_id", Integer, primary_key=True, index=True)
    name = Column("user_name", String)
    email = Column("user_email", String)
    phone_number = Column("user_phone_numeber", Numeric)
    households = relationship(
        "Household",
        secondary=Household_member.__tablename__,
        back_populates="users")
