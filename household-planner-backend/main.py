from fastapi import FastAPI

from db.database import engine
from models import chore, household, household_members, user
from routers import households, users

chore.Base.metadata.create_all(bind=engine)
household.Base.metadata.create_all(bind=engine)
household_members.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(households.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/api")
async def root():
    return {"message": "test_deploy"}
