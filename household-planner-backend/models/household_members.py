from sqlalchemy import Table, Column, ForeignKey, Integer
from db.database import Base

# household_members = Table("household_members", Base.metadata,
#                           Column("hsme_id", primary_key=True),
#                           Column("hsme_hous_id", ForeignKey("households.hous_id")),
#                           Column("hsme_user_id", ForeignKey("users.user_id")))

class Member(Base):
    __tablename__ = "household_members"

    id = Column("hsme_id", Integer, primary_key=True, index=True)
    hsme_hous_id = Column("hsme_hous_id", Integer, ForeignKey("households.hous_id"))
    hsme_user_id = Column("hsme_user_id", Integer, ForeignKey("users.user_id"))
