from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from db.database import Base
from .household_members import Member


class User(Base):
    __tablename__ = "users"

    id = Column("user_id", Integer, primary_key=True, index=True)
    name = Column("user_name", String)
    email = Column("user_email", String)
    notification_email = Column("user_notification_email", String)
    households = relationship(
        "Household",
        secondary=Member.__tablename__,
        back_populates="users")
