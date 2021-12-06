from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from schemas import members_schema
from models import household_members as hm, user as usermodel
from db.database import get_db

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
async def read_member(member_id: int, db: Session = Depends(get_db)):
    db_member = get_member_by_id(db, member_id=member_id)
    if db_member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return db_member


@router.post("/members/", tags=["members"])
async def create_member(member_create: members_schema.MemberCreate, db: Session = Depends(get_db)):
    return create_member(db=db, member=member_create)


@router.delete("/members/", tags=["members"])
async def read_member(
        householdID: int = Query(...),
        userID: int = Query(...),
        db: Session = Depends(get_db)):
    deleted = delete_member_by_ids(db=db, house_id=householdID, user_id=userID)
    if deleted is False:
        raise HTTPException(status_code=404, detail="House or User do not exist")
    return deleted


def get_members(db: Session, skip: int = 0):
    return db.query(hm.Member).offset(skip).all()


def get_member_by_id(db: Session, member_id: int):
    return db.query(hm.Member).filter(hm.Member.id == member_id).first()


def create_member(db: Session, member: members_schema.MemberCreate):
    member_user = db.query(usermodel.User).filter(usermodel.User.email == member.email).first()
    db_member = hm.Member(hsme_hous_id=member.house_id, hsme_user_id=member_user.id)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def delete_member_by_ids(db: Session, house_id: int, user_id: int):
    db_member = db.query(hm.Member).filter(and_(hm.Member.hsme_hous_id == house_id, hm.Member.hsme_user_id == user_id)).first()
    if not db_member:
        return False
    db.delete(db_member)
    db.commit()
    return db_member.id
