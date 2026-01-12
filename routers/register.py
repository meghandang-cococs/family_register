from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from models import Student, StudentClass, CurrentClasses, Family
from .auth import db_dependency, family_dependency
from sqlalchemy import func, case


router = APIRouter(
    prefix = '/student',
    tags = ['register']
)

class StudentRegisterRequest(BaseModel):
    class_id: int


def verify_student(student: Student):
    if not student: raise HTTPException(status_code=404, detail="Student not found")

    if (not student.first_name or not student.last_name or not student.dob or student.gender is None
        or not student.doctor_name or not student.doctor_phone
        or not student.ins_company or not student.ins_policy):
        raise HTTPException(
            status_code=409,
            detail="Student profile incomplete. Fill required fields before registering classes.",
        )
    
    if student is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')


async def read_classes_by_category(category_order: list, student_id: int, db: Session):
    current_year = datetime.now().year
    category_rank = case(
        {cat: i for i, cat in enumerate(category_order)},
        value=CurrentClasses.category,
        else_=len(category_order)
    )

    class_query = (
        db.query(
            CurrentClasses,
            func.count(StudentClass.student_id).label("is_selected")
        )
        .outerjoin(StudentClass, 
            (StudentClass.class_id == CurrentClasses.class_id) &
            (StudentClass.student_id == student_id) &
            (StudentClass.year == current_year) &
            ((StudentClass.paid == 0) | (StudentClass.paid.is_(None)))
        )
        .filter(CurrentClasses.category.in_(category_order))
        .group_by(CurrentClasses.class_id)
        .order_by(category_rank, CurrentClasses.weight)
    )

    results = class_query.all()

    final_data = []
    for class_obj, count in results:
        item = {c.name: getattr(class_obj, c.name) for c in class_obj.__table__.columns}
        item["class_selected"] = count
        final_data.append(item) 


    return final_data

# From select_classes.php lines 69-76
@router.get("/{student_id}/read_current_LC_classes")
async def read_current_LC_classes(student_id: int, db: db_dependency, family: family_dependency):
    student = db.query(Student).filter(Student.student_id == student_id, Student.family_id == family.get('family_id')).first()
    verify_student(student)
    category_order = ['LC', 'CSL', 'AC', 'SP-FULL','SP-HALF','SP-EC','BOOK', 'SP-lang', 'SP-AC']
    return await read_classes_by_category(category_order, student_id, db)


# From select_classes.php lines 82-88
@router.get("/{student_id}/read_current_EP_classes")
async def read_current_EP_classes(student_id: int, db: db_dependency, family: family_dependency):
    student = db.query(Student).filter(Student.student_id == student_id, Student.family_id == family.get('family_id')).first()
    verify_student(student)
    category_order = category_order = ['EP','EP-AM', 'SP-EP']
    return await read_classes_by_category(category_order, student_id, db)   


# Endpoint used by with frontend checkboxes. Frontend sends the class as input. May change to using class_id as param instead of form
# Frontend ensures there are no duplicated
@router.post("/{student_id}/select_classes")
async def select_classes(student_id: int, db: db_dependency, family: family_dependency, register: StudentRegisterRequest):
    student = db.query(Student).filter(Student.student_id == student_id, Student.family_id == family.get('family_id')).first()
    verify_student(student)
    
    current_year = datetime.now().year
    now = datetime.now()
    
    class_list = StudentClass(
        year = current_year,
        student_id = student_id,
        class_id = register.class_id,
        wait = 0,        
        paid = 0,      
        created = now,
        removed = 0
    )

    db.add(class_list)
    db.commit()

# from checkout.php 53-72
@router.get("/checkout/{family_id}")
async def view_cart(db: db_dependency, family: family_dependency):
    current_year = datetime.now().year
    cart = (((db.query(Family)
            .join(Student, Student.family_id == Family.family_id))
            .join(StudentClass, StudentClass.student_id == Student.student_id and StudentClass.wait == 0 and StudentClass.year == current_year))
            .filter(StudentClass.paid == 0)
            .filter(Family.family_id == family.get('family_id'))




    current_year = datetime.now().year

    student_ids = [
        s.student_id
        for s in db.query(Student.student_id)
                   .filter(Student.family_id == family.get('family_id'))
                   .all()
    ]
    
    return db.query(StudentClass).filter(StudentClass.student_id.in_(student_ids),
                                        StudentClass.paid == False,
                                        StudentClass.wait == False,
                                        StudentClass.year == current_year).all()