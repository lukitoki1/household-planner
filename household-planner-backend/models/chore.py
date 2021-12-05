from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import relationship

from db.database import Base


class Chore(Base):
    __tablename__ = "chores"

    id = Column("chor_id", Integer, primary_key=True, index=True, nullable=False)
    chor_hous_id = Column(Integer, ForeignKey("households.hous_id"), nullable=False)
    chor_hsme_id = Column(Integer, ForeignKey("household_members.hsme_id"), nullable=False)
    start_date = Column("chor_start_date", DateTime(timezone=True), default=func.now())
    nextOccurrence = Column("chor_occurence", Integer)
    description = Column("chor_description", String)
    status = Column("chor_status", String)
    language = Column("chor_language",String)

    household = relationship("Household", back_populates="chores")
