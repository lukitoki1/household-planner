from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from auth.auth_middleware import AuthMiddleware
from db.database import engine
from models import chore, household, household_members, user
from routers import households, users, members, chores

import firebase_admin

firebase_admin.initialize_app()

chore.Base.metadata.create_all(bind=engine)
household.Base.metadata.create_all(bind=engine)
household_members.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(AuthMiddleware)

app.include_router(households.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(chores.router, prefix="/api")


@app.get("/api")
async def root():
    return {"message": "test_deploy"}
