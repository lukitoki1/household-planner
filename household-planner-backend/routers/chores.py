from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models import chore
from routers import members, users, households
from schemas import household_schema, user_schema, chores_schema
from typing import Optional

router = APIRouter()


@router.get("/households/{house_id}/chores", tags=["chores"])
async def read_household_chores(house_id: int, name: Optional[str] = None, interval: Optional[int] = None,
                                db: Session = Depends(get_db)):
    db_chores = get_household_chores(db, house_id, name, interval)
    if db_chores is None:
        raise HTTPException(status_code=404, detail="Chores not found")
    chores_dtos_list = []
    for chore in db_chores:
        chore_dto = create_chore_dto(db, chore)
        chores_dtos_list.append(chore_dto)
    return chores_dtos_list


@router.get("/chores/{chore_id}", tags=["chores"])
async def read_chore_by_id(chore_id: int, db: Session = Depends(get_db)):
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")

    choreDto = create_chore_dto(db, db_chore)
    return choreDto


def create_chore_dto(db, db_chore):
    household_id = db_chore.chor_hous_id
    house_mem_id = db_chore.chor_hsme_id
    userDto = None
    user_id = get_user_id_from_house_members(db, house_mem_id)
    if user_id is not None:
        userDto = get_userDto_for_chore_by_id(db, user_id)

    nextOccurenceDate = calculate_next_occurence_date(db_chore.chor_start_date, db_chore.chor_occurence)
    householdDto = get_householdDto_for_chore_by_id(db, household_id)

    choreDto = chores_schema.ChoreDTO(db_chore.id, db_chore.chor_name, db_chore.chor_description, userDto, householdDto,
                                      db_chore.chor_start_date,
                                      nextOccurenceDate, db_chore.chor_occurence, db_chore.chor_language)
    return choreDto


def get_chore_by_id(db: Session, chore_id: int):
    return db.query(chore.Chore).filter(chore.Chore.id == chore_id).first()


def get_userDto_for_chore_by_id(db: Session, user_id: int):
    userDto = None
    db_user = users.get_user_by_id(db, user_id)
    if db_user is not None:
        userDto = user_schema.UserDTO(db_user.id, db_user.name, db_user.email)
    return userDto


def get_householdDto_for_chore_by_id(db: Session, house_id: int):
    householdDto = None
    db_household = households.get_household_by_id(db, house_id)
    if db_household is not None:
        householdDto = household_schema.HouseholdDTO(db_household.id, db_household.name)
    return householdDto


def get_user_id_from_house_members(db: Session, house_mem_id: int):
    db_member = members.get_member_by_id(db, house_mem_id)
    if db_member is None:
        return None
    return db_member.hsme_user_id


def get_household_chores(db: Session, house_id: int, name: Optional[str] = None, interval: Optional[int] = None):
    db_household = households.get_household_by_id(db, house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    db_chore_query = db.query(chore.Chore).filter(chore.Chore.chor_hous_id == house_id)
    if name is not None:
        db_chore_query = db.query(chore.Chore).filter(chore.Chore.chor_name == name)
    if interval is not None:
        db_chore_query = db.query(chore.Chore).filter(chore.Chore.chor_occurence == interval)

    db_chores = db_chore_query.all()
    return db_chores


def calculate_next_occurence_date(start_date, interval):
    now = datetime.now()
    print(now)
    print(start_date)
    if now <= start_date:
        return start_date
    delta = now - start_date
    delta_days = delta.days
    mod = delta_days % interval
    next_occurence_date = start_date + timedelta(days=(delta_days+(interval - mod)))
    return next_occurence_date
