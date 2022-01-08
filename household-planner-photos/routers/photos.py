from fastapi import APIRouter, HTTPException, File, UploadFile, status

from storage.storage import create_blob, exist_folder, exist_file, get_folder_files, get_file,\
    delete_file, delete_folder


router = APIRouter()


@router.post("/chores/{chore_id}/photos", tags=["chores"], status_code=status.HTTP_200_OK)
async def upload_photo(chore_id: int, photo: UploadFile = File(...)):
    content = await photo.read()
    new_blob = create_blob(str(chore_id), photo.filename)
    new_blob.upload_from_string(content)


@router.get("/chores/{chore_id}/photos", tags=["chores"])
async def get_photos(chore_id: int):
    if not exist_folder(str(chore_id)):
        return []

    return get_folder_files(str(chore_id))


@router.delete("/chores/{chore_id}/photos", tags=["chores"])
async def delete_photos(chore_id: int):
    if not exist_folder(str(chore_id)):
        return

    return delete_folder(str(chore_id))


@router.get("/chores/{chore_id}/photos/{file_name}", tags=["chores"])
async def get_photo(chore_id: int, file_name: str):
    if not exist_file(str(chore_id), file_name):
        raise HTTPException(status_code=404, detail="images not found")

    return get_file(str(chore_id), file_name)


@router.delete("/chores/{chore_id}/photos/{file_name}", tags=["chores"])
async def delete_photo(chore_id: int, file_name: str):
    if not exist_file(str(chore_id), file_name):
        return

    return delete_file(str(chore_id), file_name)






