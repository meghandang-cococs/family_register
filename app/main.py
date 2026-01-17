"""
Filename: main.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Main entry point, registers routers
"""


from fastapi import FastAPI
from .models import *
from .database import engine
from .routers import auth, family, student, register, admin, payments

from starlette.middleware.sessions import SessionMiddleware
from .routers.auth import SECRET_KEY


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key = SECRET_KEY, https_only = False)


Base.metadata.create_all(bind = engine)



@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(family.router)
app.include_router(student.router)
app.include_router(register.router)
app.include_router(admin.router)
app.include_router(payments.router)





















        


