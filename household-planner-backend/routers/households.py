from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from db.database import get_db
from operator import attrgetter
from models import household, household_members, user, chore
from schemas import household_schema
from routers import users

router = APIRouter()


@router.get("/households/", tags=["households"])
async def read_households(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id

    db_households = get_households_for_user(db, user_id)
    db_households.sort(key=attrgetter('name'))
    return db_households


@router.get("/households/{house_id}", tags=["households"])
async def read_household(house_id: int, db: Session = Depends(get_db)):
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return db_household


@router.get("/households/{house_id}/members", tags=["households"])
async def read_household_members(house_id: int, db: Session = Depends(get_db)):
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    db_household_members = get_household_members_by_house_id(db, house_id=db_household.id)
    mem_ids_list = [member.hsme_user_id for member in db_household_members]
    return db.query(user.User).filter(user.User.id.in_(mem_ids_list)).all()


@router.post("/households/{house_id}/members", tags=["households"])
async def post_household_member(house_id: int, email: str, db: Session = Depends(get_db)):
    if email is None:
        raise HTTPException(status_code=400, detail="No email parameter")
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    db_user = users.get_user_by_email(db, email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_member = household_members.Member(hsme_hous_id=db_household.id, hsme_user_id=db_user.id)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.delete("/households/{house_id}/members", tags=["households"])
async def delete_household_member(house_id: int, id: int, db: Session = Depends(get_db)):
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    db_user = users.get_user_by_id(db, user_id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_household_members = get_household_member_by_user_id_and_house_id(db, house_id=db_household.id, user_id=id)
    if db_household_members is None:
        raise HTTPException(status_code=404, detail="User is not a household member")
    db_member_chores = get_chores_by_hsme_id(db, hsme_id=db_household_members.id)
    for member_chore in db_member_chores:
        member_chore.chor_hsme_id = None
        db.add(member_chore)
    db.delete(db_household_members)
    db.commit()
    return db_user.id


@router.post("/households/", response_model=household_schema.Household, tags=["households"])
async def create_household(household_create: household_schema.HouseholdCreate, db: Session = Depends(get_db)):
    return create_household(db=db, house=household_create)


@router.put("/households/{house_id}", tags=["households"])
async def put_household(house_id: int, household_update: household_schema.HouseholdCreate,
                        db: Session = Depends(get_db)):
    house_upadted = update_household(db=db, house=household_update, house_id=house_id)
    if house_upadted is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return house_upadted


@router.delete("/households/{house_id}", tags=["households"])
async def delete_household(house_id: int, db: Session = Depends(get_db)):
    deleted = delete_household_by_id(db, house_id)
    if deleted is False:
        raise HTTPException(status_code=404, detail="Household not found")
    return house_id


def get_households_for_user(db: Session, user_id: str, skip: int = 0):
    return db.query(household.Household).join(household_members.Member).filter(
        household_members.Member.hsme_user_id == user_id).offset(skip).all()


def get_household_by_id(db: Session, house_id: int):
    return db.query(household.Household).filter(household.Household.id == house_id).first()


def get_household_members_by_house_id(db: Session, house_id: int):
    return db.query(household_members.Member).filter(household_members.Member.hsme_hous_id == house_id).all()


def get_household_member_by_user_id_and_house_id(db: Session, house_id: int, user_id: int):
    return db.query(household_members.Member).filter(household_members.Member.hsme_hous_id == house_id,
                                                     household_members.Member.hsme_user_id == user_id).first()


def create_household(db: Session, house: household_schema.HouseholdCreate):
    db_house = household.Household(name=house.name)
    db.add(db_house)
    db.commit()
    db.refresh(db_house)
    return db_house


def update_household(db, house, house_id):
    db_house = db.query(household.Household).filter(household.Household.id == house_id).first()
    if not db_house:
        return None
    house_data = house.dict(exclude_unset=True)
    for key, value in house_data.items():
        setattr(db_house, key, value)
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


def get_chores_by_hsme_id(db: Session, hsme_id: int):
    return db.query(chore.Chore).filter(chore.Chore.chor_hsme_id == hsme_id).all()
