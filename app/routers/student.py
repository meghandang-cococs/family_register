"""
Filename: student.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Endpoints handling Student object creation, update, and getting.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import desc
from datetime import datetime
from pydantic import BaseModel
from ..models import Student, StudentClass, Classes
from .auth import db_dependency, family_dependency


router = APIRouter(
    prefix = '/family',
    tags = ['student']
)

class CreateStudentRequest(BaseModel):
    first_name: str
    last_name: str
    chinese_name: str
    dob: str
    gender: str
    grade: str
    email: str
    medical_cond: str
    allergy: str
    doctor_name: str
    doctor_phone: str
    ins_company: str
    ins_policy: str


# From students.php lines 32-37 
@router.get("/student", status_code = status.HTTP_200_OK)
async def get_students_by_family(family: family_dependency, db: db_dependency):
    if family is None:
        raise HTTPException(status_code=404, detail="Family not found")
    return db.query(Student).filter(Student.family_id == family.get('family_id')).order_by(Student.dob).all()


# From add_student.php
@router.post("/student/add", status_code = status.HTTP_201_CREATED)
async def create_child(db: db_dependency, family: family_dependency, child_request: CreateStudentRequest):
    if family is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    now = datetime.utcnow()
    child_model = Student(
        first_name = child_request.first_name,
        last_name = child_request.last_name,
        chinese_name = child_request.chinese_name,
        gender = child_request.gender,
        grade = child_request.grade,
        dob = child_request.dob,
        medical_cond = child_request.medical_cond,
        allergy = child_request.allergy,
        doctor_name = child_request.doctor_name,
        doctor_phone = child_request.doctor_phone,
        ins_company = child_request.ins_company,
        ins_policy = child_request.ins_policy,
        family_id = family.get('family_id'),
        created = now,
        modified = now,
        status = 0,
        email = child_request.email,
        o_student_id = "string"
    )
    

    db.add(child_model)
    db.commit()

# From edit_student.php lines 28-63
@router.put("/student/{student_id}", status_code = status.HTTP_200_OK)
async def update_student_profile(db: db_dependency, student_id: int, child_request: CreateStudentRequest, family: family_dependency):
    student = db.query(Student).filter(Student.student_id == student_id, Student.family_id == family.get('family_id')).first()
    if student is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    profile_model = db.query(Student).filter(Student.student_id == student_id).first()
    if profile_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    profile_model.first_name = child_request.first_name
    profile_model.last_name = child_request.last_name
    profile_model.chinese_name = child_request.chinese_name
    profile_model.gender = child_request.gender
    profile_model.grade = child_request.grade
    profile_model.dob = child_request.dob
    profile_model.medical_cond = child_request.medical_cond
    profile_model.allergy = child_request.allergy
    profile_model.doctor_name = child_request.doctor_name
    profile_model.doctor_phone = child_request.doctor_phone
    profile_model.ins_company = child_request.ins_company
    profile_model.ins_policy = child_request.ins_policy
    profile_model.email = child_request.email

    db.add(profile_model)
    db.commit()


# From edit_student.php lines 65-70
@router.get("/student/{student_id}/registration_history", status_code = status.HTTP_200_OK)
async def view_student_history(db: db_dependency, student_id: int, family: family_dependency):
    student = db.query(Student).filter(Student.student_id == student_id, Student.family_id == family.get('family_id')).first()
    if student is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    history = (
        db.query(StudentClass, StudentClass.year, Classes.class_code, Classes.title, Classes.chinese_title)
        .join(Classes, Classes.class_id == StudentClass.class_id)
        .filter(StudentClass.student_id == student_id)
        .filter(StudentClass.paid != 0)
    )

    results = history.all()
    final_history = []
    for row in results:
        item = {
            "year": row.year,
            "class_code": row.class_code,
            "title": row.title,
            "chinese_title": row.chinese_title
        }
        final_history.append(item)

    return final_history

