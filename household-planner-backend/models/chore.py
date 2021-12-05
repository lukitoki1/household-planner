from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import relationship

from db.database import Base


class Chore(Base):
    __tablename__ = "chores"

    id = Column("chor_id", Integer, primary_key=True, index=True, nullable=False)
    chor_hous_id = Column(Integer, ForeignKey("households.hous_id"), nullable=False)
    chor_hsme_id = Column(Integer, ForeignKey("household_members.hsme_id"), nullable=False)
    chor_start_date = Column(DateTime(timezone=True), default=func.now())
    chor_occurence = Column(Integer)
    chor_description = Column(String)
    chor_status = Column(String)
    chor_language = Column(String)

    household = relationship("Household", back_populates="chores")
