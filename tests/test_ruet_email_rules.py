import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import UserRole
from app.security import validate_ruet_email
from fastapi import HTTPException

client = TestClient(app)

def test_validate_ruet_email_unit():
    # Student: needs 'student' and 'ruet'
    with pytest.raises(HTTPException) as exc:
        validate_ruet_email("student@gmail.com", UserRole.STUDENT)
    assert exc.value.status_code == 400
    assert "student" in exc.value.detail.lower()

    with pytest.raises(HTTPException) as exc:
        validate_ruet_email("someone@ruet.ac.bd", UserRole.STUDENT)
    assert exc.value.status_code == 400

    # Valid Student email
    validate_ruet_email("2203098@student.ruet.ac.bd", UserRole.STUDENT)
    validate_ruet_email("sifat.student@ruet.ac.bd", UserRole.STUDENT)

    # Faculty: needs 'ruet'
    with pytest.raises(HTTPException) as exc:
        validate_ruet_email("teacher@gmail.com", UserRole.FACULTY)
    assert exc.value.status_code == 400
    validate_ruet_email("teacher@cse.ruet.ac.bd", UserRole.FACULTY)

    # Staff: needs 'ruet'
    with pytest.raises(HTTPException) as exc:
        validate_ruet_email("staff@yahoo.com", UserRole.STAFF)
    assert exc.value.status_code == 400
    validate_ruet_email("electrician@ruet.ac.bd", UserRole.STAFF)


def test_register_endpoint_rejects_invalid_student_email():
    res = client.post("/auth/register", json={
        "name": "Invalid Student",
        "email": "invalid_student@gmail.com",
        "password": "password123",
        "role": "student"
    })
    assert res.status_code == 400
    assert "RUET student email" in res.json()["detail"]


def test_register_endpoint_rejects_invalid_faculty_email():
    res = client.post("/auth/register", json={
        "name": "Invalid Faculty",
        "email": "teacher@gmail.com",
        "password": "password123",
        "role": "faculty"
    })
    assert res.status_code == 400
    assert "ruet" in res.json()["detail"].lower()


def test_register_endpoint_rejects_invalid_staff_email():
    res = client.post("/auth/register", json={
        "name": "Invalid Staff",
        "email": "staff@gmail.com",
        "password": "password123",
        "role": "staff"
    })
    assert res.status_code == 400
    assert "ruet" in res.json()["detail"].lower()


def test_login_endpoint_rejects_invalid_ruet_email_format():
    res = client.post("/auth/login", json={
        "email": "fake_student@gmail.com",
        "password": "password123",
        "role": "student"
    })
    assert res.status_code == 400
    assert "ruet" in res.json()["detail"].lower()
