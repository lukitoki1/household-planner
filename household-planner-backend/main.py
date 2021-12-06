from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import engine
from models import chore, household, household_members, user
from routers import households, users, members

chore.Base.metadata.create_all(bind=engine)
household.Base.metadata.create_all(bind=engine)
household_members.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
"http://localhost:8000",
"http://localhost:3000",
"https://household-planner-333519.uc.r.appspot.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(households.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(members.router, prefix="/api")


@app.get("/api")
async def root():
    return {"message": "test_deploy"}
