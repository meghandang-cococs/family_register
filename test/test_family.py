"""
Filename: test_family.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Unit tests for family.py
"""

from .utils import *
from app.routers.auth import get_db, get_current_family
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_family] = override_get_current_family


def test_create_family(test_family):
    request_data={
        'email': 'tester@e.com',
        'password':'1234',
        'check_password': '1234'
    }

    response = client.post('/family/profile/create', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Family).filter(Family.email == 'tester@e.com').first()
    assert model.email == request_data.get('email')
    assert model.password == request_data.get('password')


def test_create_family_fail(test_family):
    request_data={
        'email': 'tester@e.com',
        'password':'12345',
        'check_password': '1234'
    }

    response = client.post('/family/profile/create', json=request_data)
    assert response.status_code == 400


def test_return_family(test_family):
    response = client.get("/family/profile/view")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['email'] == 'test1@e.com'
    assert response.json()['father_fname'] == 'Father'
    assert response.json()['father_lname'] == 'Test'
    assert response.json()['mother_fname'] == 'Mother'
    assert response.json()['mother_lname'] == 'Test'
    assert response.json()['phone'] == '7777777777'


def test_return_volunteer(test_family, test_voluneer_activity, test_volunteer_activity_year, test_family_year):
    response = client.get("/family/profile/volunteer")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'year': 2026,
                                'code': 1,
                                'name': "Some Activity"}]


def test_update_family(test_family):
    response = client.put(
        "/family/profile/edit",
        json={
            "email": "test1@e.com",
            "father_fname": "Father",
            "father_lname": "Test",
            "mother_fname": "Mother",
            "mother_lname": "Test",
            "father_cname": "",
            "mother_cname": "",
            "address": "",
            "address2": "",
            "city": "Some City",  # field being updated
            "state": "",
            "zip": "",
            "country": "US",
            "email2": "test2@e.com",  # field being updated
            "phone": "7777777777",
            "phone2": "",
            "education": 0,
            "income": 0,
            "main_lang_id": "",
            "ecp_name": "",
            "ecp_relation": "",
            "ecp_phone": "",
            "medical_cond": "",
            "allergy": 0,
            "doctor_name": "",
            "doctor_phone": "",
            "ins_company": "",
            "ins_policy": ""
        })
    assert response.status_code == status.HTTP_200_OK
