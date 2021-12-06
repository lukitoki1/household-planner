from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import relationship

from db.database import Base


class Chore(Base):
    __tablename__ = "chores"

    id = Column("chor_id", Integer, primary_key=True, index=True, nullable=False)

    chor_hous_id = Column("chor_hous_id", Integer, ForeignKey("households.hous_id"), nullable=False)
    chor_hsme_id = Column("chor_hsme_id", Integer, ForeignKey("household_members.hsme_id"), nullable=False)
    chor_start_date = Column("chor_start_date", DateTime(timezone=True), default=func.now())
    chor_occurence = Column("chor_occurence", Integer)
    chor_name = Column("chor_name", String)
    chor_description = Column("chor_description", String)
    chor_status = Column("chor_status", String)
    chor_language = Column("chor_language", String)

    household = relationship("Household", back_populates="chores")
