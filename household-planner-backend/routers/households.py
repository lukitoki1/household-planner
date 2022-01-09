from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.requests import Request

from db.database import get_db
from operator import attrgetter
from models import household, household_members, user as usermodel, chore, household_members as hm
from schemas import household_schema, members_schema
from routers import users
import os
import requests

router = APIRouter()

photo_service = os.getenv("PHOTOS_SERVICE")


@router.get("/households/", tags=["households"])
async def read_households(request: Request, db: Session = Depends(get_db)):
    user_id = get_user_id_from_request(request)
    db_households = get_households_for_user(db, user_id)
    db_households.sort(key=attrgetter('name'))
    return db_households


@router.get("/households/{house_id}", tags=["households"])
async def read_household(request: Request, house_id: int, db: Session = Depends(get_db)):
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    if not check_household_membership(request, db, house_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    return db_household


@router.get("/households/{house_id}/members", tags=["household-members"])
async def read_household_members(request: Request, house_id: int, db: Session = Depends(get_db)):
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    if not check_household_membership(request, db, house_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    db_household_members = get_household_members_by_house_id(db, house_id=db_household.id)
    user_list = []
    for elem in db_household_members:
        user = db.query(usermodel.User).filter(usermodel.User.id == elem.hsme_user_id).first()
        member_dto = members_schema.MemberDTO(user.id, user.name, user.email, elem.is_owner)
        user_list.append(member_dto)
    return user_list


@router.post("/households/{house_id}/members", tags=["household-members"])
async def post_household_member(request: Request, house_id: int, email: str, db: Session = Depends(get_db)):
    if email is None:
        raise HTTPException(status_code=400, detail="No email parameter")
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    db_user = users.get_user_by_email(db, email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not check_household_membership(request, db, house_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    db_member = household_members.Member(hsme_hous_id=db_household.id, hsme_user_id=db_user.id, is_owner=0)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.delete("/households/{house_id}/members", tags=["household-members"])
async def delete_household_member(request: Request, house_id: int, id: int, db: Session = Depends(get_db)):
    db_household = get_household_by_id(db, house_id=house_id)
    if db_household is None:
        raise HTTPException(status_code=404, detail="Household not found")
    db_user = users.get_user_by_id(db, user_id=id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_household_members = get_household_member_by_user_id_and_house_id(db, house_id=db_household.id, user_id=id)
    if db_household_members is None:
        raise HTTPException(status_code=404, detail="User is not a household member")
    if check_household_ownership(request, db, house_id, id):
        raise HTTPException(status_code=403, detail="You can not delete house owner!")
    db_member_chores = get_chores_by_hsme_id(db, hsme_id=db_household_members.id)
    for member_chore in db_member_chores:
        member_chore.chor_hsme_id = None
        db.add(member_chore)
    db.delete(db_household_members)
    db.commit()
    return db_user.id


@router.post("/households/", response_model=household_schema.Household, tags=["households"])
async def create_household(request: Request, household_create: household_schema.HouseholdCreate,
                           db: Session = Depends(get_db)):
    created = create_household(request=request, db=db, house=household_create)
    if created is None:
        raise HTTPException(status_code=404, detail="Household creation error!")
    return created


@router.put("/households/{house_id}", tags=["households"])
async def put_household(request: Request, house_id: int, household_update: household_schema.HouseholdCreate,
                        db: Session = Depends(get_db)):
    if not check_household_membership(request, db, house_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    if not check_household_ownership(request, db, house_id, -1):
        raise HTTPException(status_code=403, detail="Not a house owner")
    house_upadted = update_household(db=db, house=household_update, house_id=house_id)
    if house_upadted is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return house_upadted


@router.delete("/households/{house_id}", tags=["households"])
async def delete_household(request: Request, house_id: int, db: Session = Depends(get_db)):
    db_house = db.query(household.Household).filter(household.Household.id == house_id).first()
    if db_house is None:
        raise HTTPException(status_code=404, detail="Household not found")
    if not check_household_membership(request, db, house_id):
            raise HTTPException(status_code=403, detail="Not a house member")
    if not check_household_ownership(request, db, house_id, -1):
        raise HTTPException(status_code=403, detail="Not a house owner")
    delete_household_chores(db, house_id)
    delete_household_members(db, house_id)
    db.delete(db_house)
    db.commit()
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


def create_household(request: Request, db: Session, house: household_schema.HouseholdCreate):
    user_id = get_user_id_from_request(request)
    db_house = household.Household(name=house.name)
    db.add(db_house)
    db.commit()
    db.refresh(db_house)
    create_owner(request, db, db_house.id, user_id)
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


def get_user_id_from_request(request: Request):
    # user_id = 1
    user_id = request.state.user_id
    return user_id


def check_household_membership(request: Request, db: Session, house_id: int):
    db_household_members = get_household_members_by_house_id(db, house_id=house_id)
    mem_ids_list = [member.hsme_user_id for member in db_household_members]
    user_id = get_user_id_from_request(request)
    if user_id not in mem_ids_list:
        return False
    return True


def check_household_ownership(request: Request, db: Session, house_id: int, user_id: int):
    db_household_members = get_household_members_by_house_id(db, house_id=house_id)
    if user_id == -1:
        user_id = get_user_id_from_request(request)
    match = [elem for elem in db_household_members if elem.hsme_user_id == user_id]
    if len(match) < 1:
        return False
    if match[0].is_owner != 1:
        return False
    return True


def create_owner(request: Request, db: Session, house_id: int, user_id: int):
    if user_id == -1:
        user_id = get_user_id_from_request(request)
    member_user = db.query(usermodel.User).filter(usermodel.User.id == user_id).first()
    db_member = household_members.Member(hsme_hous_id=house_id, hsme_user_id=member_user.id, is_owner=1)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return True


def delete_household_chores(db: Session, house_id: int):
    house_chores = db.query(chore.Chore).filter(chore.Chore.chor_hous_id == house_id).all()
    for h_chore in house_chores:
        db.delete(h_chore)
        response = requests.delete(
            f"{photo_service}/photos/chores/{h_chore.id}/photos")
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code)
    db.commit()


def delete_household_members(db: Session, house_id: int):
    found_members = db.query(household_members.Member).filter(household_members.Member.hsme_hous_id == house_id).all()
    for member in found_members:
        db.delete(member)
    db.commit()


def get_chores_by_hsme_id(db: Session, hsme_id: int):
    return db.query(chore.Chore).filter(chore.Chore.chor_hsme_id == hsme_id).all()


def get_household_member_by_id(db: Session, member_id: int):
    return db.query(hm.Member).filter(hm.Member.id == member_id).first()