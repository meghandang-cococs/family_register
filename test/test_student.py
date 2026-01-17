"""
Filename: test_student.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Unit tests for student.py
"""

from .utils import *
from app.routers.auth import get_db, get_current_family
from fastapi import status
from datetime import date

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_family] = override_get_current_family

now = datetime.now()

def test_get_students_by_family(test_family, test_student):
    response = client.get("/family/student")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(item["first_name"] == "Student" for item in data)
    assert any(item["student_id"] == 1 for item in data)
    assert any(item["allergy"] == "Example" for item in data)

def test_create_child(test_family, test_student):
    request_data = {
        "student_id": "2",
        "o_student_id": "",
        "family_id": "1",
        "first_name": "Student",
        "last_name": "Test",
        "chinese_name": "同学",
        "dob" :"01/01/2000",
        "gender": "M",
        "grade": "0",
        "status": 1,
        "email": "test@e.com",
        "medical_cond": "Example",
        "allergy": "Example",
        "doctor_name": "Example",
        "doctor_phone": "Example",
        "ins_company": "Example",
        "ins_policy": "Example"
    } 
                    
    response = client.post("/family/student/add", json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    try:
        model = db.query(Student).filter(Student.student_id == 2).first()
        assert model.email == request_data.get('email')
        assert model.first_name == request_data.get('first_name')
    finally:
        db.close()


def test_update_student_family_profile(test_family, test_student):
    response = client.put(
        "/family/student/1",
        json={
            "student_id": "1",
            "o_student_id": "",
            "family_id": "1",
            "first_name": "Student",
            "last_name": "Test",
            "chinese_name": "同学",
            "dob" :"01/01/2000",
            "gender": "M",
            "grade": "0",
            "status": 1,
            "email": "test@e.com",
            "medical_cond": "Example",
            "allergy": "Peanut",
            "doctor_name": "Example",
            "doctor_phone": "Example",
            "ins_company": "Example",
            "ins_policy": "Example"
        })
    assert response.status_code == status.HTTP_200_OK
    db = TestingSessionLocal()
    try:
        model = db.query(Student).filter(Student.student_id == 1).first()
        assert model.allergy == "Peanut"
    finally:
        db.close()


def test_view_student_history(test_family, test_student, test_classes, test_student_class_paid):
    response = client.get("/family/student/1/registration_history")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    
    row = data[0]
    assert row["class_code"] == "1" 
    assert row["title"] == "Level 1"
    assert row["chinese_title"] == "东西" 