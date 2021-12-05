from sqlalchemy import Table, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from db.database import Base

class Household_member(Base):
    __tablename__ = "household_members"

    id = Column("hous_id", Integer, primary_key=True, index=True)
    house_id = Column("hsme_hous_id", ForeignKey("households.hous_id"))
    user_id = Column("hsme_user_id", ForeignKey("users.user_id"))
