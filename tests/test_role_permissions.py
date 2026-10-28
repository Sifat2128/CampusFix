import pytest
from app.models import UserRole
from app.security import validate_ruet_email
from fastapi import HTTPException

def test_all_roles_validation():
    # 1. Students require 'student' and 'ruet'
    validate_ruet_email("2203098@student.ruet.ac.bd", UserRole.STUDENT)
    with pytest.raises(HTTPException):
        validate_ruet_email("teacher@ruet.ac.bd", UserRole.STUDENT)

    # 2. Faculty require 'ruet'
    validate_ruet_email("teacher@dept.ruet.ac.bd", UserRole.FACULTY)
    with pytest.raises(HTTPException):
        validate_ruet_email("teacher@gmail.com", UserRole.FACULTY)

    # 3. Staff require 'ruet'
    validate_ruet_email("electrician@ruet.ac.bd", UserRole.STAFF)
    with pytest.raises(HTTPException):
        validate_ruet_email("staff@yahoo.com", UserRole.STAFF)
