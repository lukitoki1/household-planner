from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from schemas import members_schema
from models import household_members as hm, user as usermodel
from db.database import get_db
from starlette.requests import Request
from models import household_members

router = APIRouter()


@router.get("/members/", tags=["members"])
async def read_members(db: Session = Depends(get_db)):
    db_members = get_members(db)
    return db_members


# @router.get("/members/", tags=["members"])
# async def read_member(user_id: int = Query(...,max_length=20), house_id: int = Query(..., max_length=20), db: Session = Depends(get_db)):
#     db_member = get_member_by_ids(db, user_id=user_id, house_id=house_id)
#     if db_member is None:
#         raise HTTPException(status_code=404, detail="Member not found")
#     return db_member

@router.get("/members/{member_id}", tags=["members"])
async def read_member(request: Request, member_id: int, db: Session = Depends(get_db)):
    db_member = get_member_by_id(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    house_id = db_member.hsme_hous_id
    if not check_household_membership(request, db, house_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    return db_member


@router.post("/members/", tags=["members"])
async def create_member(request: Request, member_create: members_schema.MemberCreate, db: Session = Depends(get_db)):
    user_id = get_user_id_from_request()
    user_members = get_member_by_user_id(db, user_id)
    match = [x for x in user_members if x.hsme_house_id == member_create.house_id]
    if len(match) == 0:
        raise HTTPException(status_code=403, detail="Not a house member")
    return create_member(db=db, member=member_create)


@router.delete("/members/", tags=["members"])
async def delete_member(request: Request,
                        householdID: int = Query(...),
                        userID: int = Query(...),
                        db: Session = Depends(get_db)):
    user_id = get_user_id_from_request()
    user_members = get_member_by_user_id(db, user_id)
    match = [x for x in user_members if x.hsme_house_id == get_member_by_ids(db=db, house_id=householdID, user_id=userID).house_id]
    if len(match) == 0:
        raise HTTPException(status_code=403, detail="Not a house member")
    if not check_household_membership(request, db, match[0]):
        if not check_household_ownership(request, db, match[0], user_id):
            raise HTTPException(status_code=403, detail="Not a house member")
    deleted = delete_member_by_ids(db=db, house_id=householdID, user_id=userID)
    if deleted is False:
        raise HTTPException(status_code=404, detail="House or User do not exist")
    return deleted


def get_members(db: Session, skip: int = 0):
    return db.query(hm.Member).offset(skip).all()


def get_member_by_id(db: Session, member_id: int):
    return db.query(hm.Member).filter(hm.Member.id == member_id).first()


def get_member_by_user_id(db: Session, user_id: int):
    return db.query(hm.Member).filter(hm.Member.hsme_user_id == user_id).all()


def create_member(db: Session, member: members_schema.MemberCreate):
    member_user = db.query(usermodel.User).filter(usermodel.User.email == member.email).first()
    db_member = hm.Member(hsme_hous_id=member.house_id, hsme_user_id=member_user.id, is_owner=0)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def delete_member_by_ids(db: Session, house_id: int, user_id: int):
    db_member = db.query(hm.Member).filter(
        and_(hm.Member.hsme_hous_id == house_id, hm.Member.hsme_user_id == user_id)).first()
    if not db_member:
        return False
    db.delete(db_member)
    db.commit()
    return db_member.id

def get_member_by_ids(db: Session, house_id: int, user_id: int):
    return db.query(hm.Member).filter(
        and_(hm.Member.hsme_hous_id == house_id, hm.Member.hsme_user_id == user_id)).first()

#Check household membership
def check_household_membership(request: Request, db: Session, house_id: int):
    db_household_members = get_household_members_by_house_id(db, house_id=house_id)
    mem_ids_list = [member.hsme_user_id for member in db_household_members]
    user_id = get_user_id_from_request(request)
    if user_id not in mem_ids_list:
        return False
    return True


def check_household_ownership(request: Request, db: Session, house_id: int, user_id: int):
    db_household_members = get_household_members_by_house_id(db, house_id=house_id)
    match = [elem for elem in db_household_members if elem.hsme_user_id == user_id]
    if match.is_owner != 1:
        return False
    return True


def get_user_id_from_request(request: Request):
    # user_id = 1
    user_id = request.state.user_id
    return user_id


def get_household_members_by_house_id(db: Session, house_id: int):
    return db.query(household_members.Member).filter(household_members.Member.hsme_hous_id == house_id).all()
