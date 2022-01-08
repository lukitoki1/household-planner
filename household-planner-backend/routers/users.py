from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import user_schema
from models import user as usermodel
from db.database import get_db

router = APIRouter()


@router.get("/users/", tags=["users"])
async def read_users(db: Session = Depends(get_db)):
    db_users = get_users(db)
    return db_users


@router.get("/users/{user_id}", tags=["users"])
async def read_users(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/users/", response_model=user_schema.User, tags=["users"])
async def create_user(user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user_create)


@router.delete("/users/{user_id}", tags=["users"])
async def read_user(user_id: int, db: Session = Depends(get_db)):
    deleted = delete_user_by_id(db, user_id)
    if deleted is False:
        raise HTTPException(status_code=404, detail="User not found")
    return user_id


@router.put("/users/{user_id}", response_model=user_schema.User, tags=["users"])
async def create_user(user_id: int, user_update: user_schema.UserUpdate, db: Session = Depends(get_db)):
    user_updated = update_user(db=db, user=user_update, user_id=user_id)
    if user_updated is None:
        raise HTTPException(status_code=404, detail="User not found!")
    return user_updated


def get_users(db: Session, skip: int = 0):
    return db.query(usermodel.User).offset(skip).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(usermodel.User).filter(usermodel.User.id == user_id).first()


def get_user_by_email(db: Session, user_email: str):
    return db.query(usermodel.User).filter(usermodel.User.email == user_email).first()


def create_user(db: Session, user: user_schema.UserCreate):
    db_user = usermodel.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user_by_id(db: Session, user_id: int):
    db_user = db.query(usermodel.User).filter(usermodel.User.id == user_id).first()
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def update_user(db: Session, user: user_schema.UserUpdate, user_id: int):
    db_user = db.query(usermodel.User).filter(usermodel.User.id == user_id).first()
    if not db_user:
        return None
    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
