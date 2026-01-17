from fastapi import APIRouter
from ..models import Student, Family
from .auth import db_dependency

router = APIRouter(
    prefix = '/admin',
    tags = ['admin']
)

@router.get("/read_families")
async def read_all_families(db: db_dependency):
    return db.query(Family).all()

@router.get("/read_students")
async def read_all_students(db: db_dependency):
    return db.query(Student).all()