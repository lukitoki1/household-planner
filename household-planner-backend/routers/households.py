from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import household_schema
from models import household
from db.database import get_db

router = APIRouter()


@router.get("/households/", tags=["households"])
async def read_households(db: Session = Depends(get_db)):
    db_households = get_households(db)
    return db_households


@router.get("/households/{house_id}", tags=["households"])
async def read_household(house_id: int, db: Session = Depends(get_db)):
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return db_household


@router.post("/households/", response_model=household_schema.Household, tags=["households"])
async def create_household(household_create: household_schema.HouseholdCreate, db: Session = Depends(get_db)):
    return create_household(db=db, house=household_create)


@router.delete("/households/{house_id}", tags=["households"])
async def read_household(house_id: int, db: Session = Depends(get_db)):
    deleted = delete_household_by_id(db, house_id)
    if deleted is False:
        raise HTTPException(status_code=404, detail="Household not found")
    return house_id


def get_households(db: Session, skip: int = 0):
    return db.query(household.Household).offset(skip).all()


def get_household_by_id(db: Session, house_id: int):
    return db.query(household.Household).filter(household.Household.id == house_id).first()


def create_household(db: Session, house: household_schema.HouseholdCreate):
    db_house = household.Household(name=house.name)
    db.add(db_house)
    db.commit()
    db.refresh(db_house)
    return db_house


def delete_household_by_id(db: Session, house_id: int):
    db_house = db.query(household.Household).filter(household.Household.id == house_id).first()
    if not db_house:
        return False
    db.delete(db_house)
    db.commit()
    return True
