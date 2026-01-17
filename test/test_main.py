"""
Filename: test_main.py
Author: Meghan Dang
Date: 2025-01-16
Version: 1.0
Description: Unit tests for main.py
"""

from fastapi.testclient import TestClient
from app.main import app
from fastapi import status

client = TestClient(app)

def test_return_health_check():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'Healthy'}