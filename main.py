
from fastapi import FastAPI
from models import *
from database import engine, SessionLocal
from routers import auth, family, student, register, admin


app = FastAPI()

Base.metadata.create_all(bind = engine)

app.include_router(auth.router)
app.include_router(family.router)
app.include_router(student.router)
app.include_router(register.router)
app.include_router(admin.router)





















        


