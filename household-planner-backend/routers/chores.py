from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session

from db.database import get_db
from models import chore, household_members
from routers import members, users, households
from schemas import household_schema, user_schema, chores_schema
from typing import Optional
from dateutil.parser import isoparse
import httpx
import requests
import os
import urllib.parse
import json
from starlette.requests import Request

router = APIRouter()
client = httpx.AsyncClient()

photo_service = os.getenv("PHOTOS_SERVICE")
translation_service = os.getenv("TRANSLATION_SERVICE")


@router.get("/households/{house_id}/chores", tags=["chores"])
async def read_household_chores(request: Request, house_id: int, name: Optional[str] = None, interval: Optional[int] = None,
                                db: Session = Depends(get_db)):
    db_chores = get_household_chores(db, house_id, name, interval)
    if db_chores is None:
        raise HTTPException(status_code=404, detail="Chores not found")
    if check_household_membership(request, db, house_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    chores_dtos_list = []
    for chore in db_chores:
        chore_dto = create_chore_dto(db, chore)
        chores_dtos_list.append(chore_dto)
    return chores_dtos_list


@router.get("/chores/{chore_id}", tags=["chores"])
async def read_chore_by_id(request: Request, chore_id: int, db: Session = Depends(get_db)):
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    if check_household_membership(request, db, house_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    choreDto = create_chore_dto(db, db_chore)
    return choreDto


@router.get("/chores/{chore_id}/description", tags=["chores"])
async def read_chore_translation(request: Request, chore_id: int, language: str, db: Session = Depends(get_db)):
    # pobranie opisu z bazy
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    if check_household_membership(request, db, chore_id.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    choreDto = create_chore_dto(db, db_chore)
    choreDesc = choreDto.description
    # utworzenie url do zapytania mikroserwisu i wysłanie zapytania
    text = urllib.parse.quote(choreDesc)
    url = f"{translation_service}/api/translation?lang={language}&text={text}"
    res = await make_translation_request(url)
    if res.status_code < 200 or res.status_code > 299:
        res_det = json.loads(res.text)
        raise HTTPException(status_code=404, detail=res_det['detail'])
    return res.json()


async def make_translation_request(url: str):
    req = client.build_request('get', url)
    res = client.send(req)
    # odbiór odpowiedzi
    return await res


@router.post("/households/{house_id}/chores", tags=["chores"])
async def post_chore(request: Request, house_id: int, chore_create: chores_schema.ChoreCreate, db: Session = Depends(get_db)):
    if check_household_membership(request, db, house_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    return create_chore(house_id, chore_create, db)


@router.post("/chores/{chore_id}/assignee", tags=["chores"])
async def assign_user_to_chore(request: Request, chore_id: int, email: str, db: Session = Depends(get_db)):
    if email is None:
        raise HTTPException(status_code=400, detail="No email parameter")
    db_chore = get_chore_by_id(db, chore_id)
    if check_household_membership(request, db, db_chore.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    return add_user_to_chore(chore_id, email, db)


@router.delete("/chores/{chore_id}/assignee", tags=["chores"])
async def remove_user_from_chore(request: Request, chore_id: int, db: Session = Depends(get_db)):
    db_chore = get_chore_by_id(db, chore_id)
    if check_household_membership(request, db, db_chore.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    return delete_chore_assignee(chore_id, db)


@router.put("/chores/{chore_id}", tags=["chores"])
async def put_chore(request: Request, chore_id: int, chore_edit: chores_schema.ChoreEdit, db: Session = Depends(get_db)):
    db_chore = get_chore_by_id(db, chore_id)
    if check_household_membership(request, db, db_chore.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    db_chore = update_chore(chore_id, chore_edit, db)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    return db_chore


@router.delete("/chores/{chore_id}", tags=["chores"])
async def delete_chore_by_id(request: Request, chore_id: int, db: Session = Depends(get_db)):
    deleted = delete_chore_by_id(db, chore_id)
    if deleted is False:
        raise HTTPException(status_code=404, detail="Chore not found")
    db_chore = get_chore_by_id(db, chore_id)
    if check_household_membership(request, db, db_chore.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    return chore_id


@router.post("/chores/{chore_id}/photos", tags=["chores"], status_code=status.HTTP_200_OK)
async def upload_photo(request: Request, chore_id: int, db: Session = Depends(get_db), photo: UploadFile = File(...)):
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    if check_household_membership(request, db, db_chore.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    content = await photo.read()
    response = requests.post(f"{photo_service}/photos/chores/{chore_id}/photos",
                             files={"photo": (photo.filename, content, photo.content_type)})

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)


@router.get("/chores/{chore_id}/photos", tags=["chores"])
async def get_photos(request: Request, chore_id: int, db: Session = Depends(get_db)):
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    if check_household_membership(request, db, db_chore.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    response = requests.get(
        f"{photo_service}/photos/chores/{chore_id}/photos")

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)

    return response.json()


@router.get("/chores/{chore_id}/photos/{file_name}", tags=["chores"])
async def get_photo(request: Request, chore_id: int, file_name: str, db: Session = Depends(get_db)):
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    if check_household_membership(request, db, db_chore.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    response = requests.get(
        f"{photo_service}/photos/chores/{chore_id}/photos/{file_name}")

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)

    return response.json()


@router.delete("/chores/{chore_id}/photos/{file_name}", tags=["chores"])
async def delete_photo(request: Request, chore_id: int, file_name: str, db: Session = Depends(get_db)):
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    if check_household_membership(request, db, db_chore.chor_hous_id):
        raise HTTPException(status_code=403, detail="Not a house member")
    response = requests.delete(
        f"{photo_service}/photos/chores/{chore_id}/photos/{file_name}")

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)


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


def create_chore(house_id: int, chore_create: chores_schema.ChoreCreate, db: Session):
    db_house = households.get_household_by_id(db, house_id)
    if db_house is None:
        raise HTTPException(status_code=404, detail="Household not found")

    date_string = chore_create.startDate
    date = isoparse(date_string)
    db_chores = chore.Chore(chor_hous_id=house_id, chor_hsme_id=None, chor_start_date=date,
                            chor_occurence=chore_create.intervalDays, chor_name=chore_create.name,
                            chor_description=chore_create.description, chor_status=None,
                            chor_language=chore_create.language)
    db.add(db_chores)
    db.commit()
    db.refresh(db_chores)
    return create_chore_dto(db, db_chores)


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
    if now <= start_date:
        return start_date
    delta = now - start_date
    delta_days = delta.days
    mod = delta_days % interval
    next_occurence_date = start_date + timedelta(days=(delta_days + (interval - mod)))
    return next_occurence_date


def delete_chore_by_id(db: Session, chore_id: int):
    db_chore = db.query(chore.Chore).filter(chore.Chore.id == chore_id).first()
    if not db_chore:
        return False
    db.delete(db_chore)
    db.commit()
    return True


def update_chore(chore_id: int, chore_edit: chores_schema.ChoreEdit, db: Session):
    db_chore = get_chore_by_id(db, chore_id)
    if not db_chore:
        return None
    chore_data = chore_edit.dict(exclude_unset=True)
    if "name" in chore_data:
        chore_data["chor_name"] = chore_data.pop("name")
    if "description" in chore_data:
        chore_data["chor_description"] = chore_data.pop("description")
    if "startDate" in chore_data:
        start_date_string = chore_data.pop("startDate")
        chore_data["chor_start_date"] = isoparse(start_date_string)
    if "intervalDays" in chore_data:
        chore_data["chor_occurence"] = chore_data.pop("intervalDays")
    if "language" in chore_data:
        chore_data["chor_language"] = chore_data.pop("language")
    for key, value in chore_data.items():
        setattr(db_chore, key, value)
    db.add(db_chore)
    db.commit()
    db.refresh(db_chore)
    return create_chore_dto(db, db_chore)


def add_user_to_chore(chore_id: int, assignee: str, db: Session):
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    db_user = users.get_user_by_email(db, assignee)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    house_id = db_chore.chor_hous_id
    db_house = households.get_household_by_id(db, house_id)
    if db_house is None:
        raise HTTPException(status_code=404, detail="Household not found")
    db_house_member = db.query(household_members.Member).filter(
        household_members.Member.hsme_user_id == db_user.id,
        household_members.Member.hsme_hous_id == db_house.id).first()
    if db_house_member is None:
        raise HTTPException(status_code=404, detail="The user does not belong to the same house as the chore")
    db_chore.chor_hsme_id = db_house_member.id
    db.add(db_chore)
    db.commit()
    db.refresh(db_chore)
    return create_chore_dto(db, db_chore)


def delete_chore_assignee(chore_id: int, db: Session):
    db_chore = get_chore_by_id(db, chore_id)
    if db_chore is None:
        raise HTTPException(status_code=404, detail="Chore not found")
    db_chore.chor_hsme_id = None
    db.add(db_chore)
    db.commit()
    db.refresh(db_chore)
    return chore_id

#Check household membership
def get_user_id_from_request(request: Request):
    user_id = 5
    # user_id = request.state.user_id
    return user_id

def get_household_members_by_house_id(db: Session, house_id: int):
    return db.query(household_members.Member).filter(household_members.Member.hsme_hous_id == house_id).all()

def check_household_membership(request: Request, db: Session, house_id: int):
    db_household_members = get_household_members_by_house_id(db, house_id=house_id)
    mem_ids_list = [member.hsme_user_id for member in db_household_members]
    user_id = get_user_id_from_request(request)
    if user_id not in mem_ids_list:
        return False
    return True

def check_household_ownership(request: Request, db: Session, house_id: int):
    db_household_members = get_household_members_by_house_id(db, house_id=house_id)
    user_id = get_user_id_from_request(request)
    match = [elem for elem in db_household_members if elem.hsme_user_id==user_id]
    if match.is_owner != 1:
        return False
    return True
