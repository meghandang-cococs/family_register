"""
Filename: test_register.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Unit tests for register.py
"""

from .utils import *
from app.routers.auth import get_db, get_current_family
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_family] = override_get_current_family


def test_read_current_LC_classes(test_family, test_student, test_student_class_unpaid, test_current_classes_1):
    response = client.get("/student/1/read_current_LC_classes")
    assert response.status_code == status.HTTP_200_OK 

def test_read_current_LC_classes_fail(test_family, test_student, test_student_class_unpaid, test_current_classes_1):
    response = client.get("/student/99/read_current_LC_classes")
    assert response.status_code == 404

def test_read_current_EP_classes(test_family, test_student, test_student_class_unpaid, test_current_classes_2):
    response = client.get("/student/1/read_current_EP_classes")
    assert response.status_code == status.HTTP_200_OK

def test_select_classes(test_family, test_student):
    request_data={
        'class_id': '1'
    }

    response = client.post("/student/1/select_classes", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(StudentClass).filter(StudentClass.student_id == 1, StudentClass.class_id == int(request_data.get('class_id'))).first()
    assert model.student_id == 1
    assert model.class_id == int(request_data.get('class_id'))

