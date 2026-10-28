from fastapi import Depends,HTTPException,status
from . import models,schemas,oAuth
from sqlalchemy.orm import Session
from .database import get_db 

def require_student(db:Session,current_user =  Depends(oAuth.get_user)):
    role = db.query(models.User.role).filter(models.User.id == current_user.id).first()
    if role != models.UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not Authorized")
    return True

def require_faculty(db:Session,current_user =  Depends(oAuth.get_user)):
    role = db.query(models.User.role).filter(models.User.id == current_user.id).first()
    if role != models.UserRole.FACULTY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not Authorized")
    return True
    
def require_staff(db:Session,current_user =  Depends(oAuth.get_user)):
    role = db.query(models.User.role).filter(models.User.id == current_user.id).first()
    if role != models.UserRole.STAFF:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not Authorized")
    return True

def require_admin(db:Session,current_user =  Depends(oAuth.get_user)):
    role = db.query(models.User.role).filter(models.User.id == current_user.id).first()
    if role != models.UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not Authorized")
    return True

def require_verified(db:Session,current_user =  Depends(oAuth.get_user)):
    if not current_user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized")
    return True
