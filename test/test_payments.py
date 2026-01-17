"""
Filename: test_student.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Unit tests for payments.py
"""

from .utils import *
from app.routers.auth import get_db, get_current_family
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_family] = override_get_current_family


def test_view_cart(test_family, test_student, test_student_class_unpaid, test_classes):
    response = client.get("/family/checkout")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(item["first_name"] == "Student" for item in data)
    assert any(item["class_id"] == 1 for item in data)
    assert any(item["title"] == "Level 1" for item in data)

def test_view_payments(test_family, test_order_paid, test_order_student_class):
    response = client.get("/family/payments")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(item["order_id"] == 1 for item in data)


def test_view_order_details_success(test_family, test_order, test_student, test_order_student_class):
    # Mark order as paid to pass filter
    db = TestingSessionLocal()
    order = db.query(Order).filter(Order.order_id == test_order.order_id).first()
    order.paid = datetime.utcnow()
    db.commit()
    response = client.get(f"/family/payments/view_order_details/{test_order.order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == test_order.order_id
    assert data["family_id"] == test_family.family_id
    assert "number_of_classes" in data


def test_view_order_details_not_found(test_family):
    response = client.get("/family/payments/view_order_details/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_view_order_classes_success(test_family, test_order, test_student, test_order_student_class, test_student_class_unpaid, test_classes):
    # Mark order as paid to pass filter
    db = TestingSessionLocal()
    order = db.query(Order).filter(Order.order_id == test_order.order_id).first()
    order.paid = datetime.utcnow()
    db.commit()
    response = client.get(f"/family/payments/view_order_classes/{test_order.order_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any("student_id" in item for item in data)


def test_view_order_classes_not_found(test_family):
    response = client.get("/family/payments/view_order_classes/9999")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0].get("name") == "Total"
    assert data[0].get("Price") == 0


