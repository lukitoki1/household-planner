from sqlalchemy import Table, Column, ForeignKey
from db.database import Base

household_members = Table("household_members", Base.metadata,
                          Column("hsme_id", primary_key=True),
                          Column("hsme_hous_id", ForeignKey("households.hous_id")),
                          Column("hsme_user_id", ForeignKey("users.user_id")))
