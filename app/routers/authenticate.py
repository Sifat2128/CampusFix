from pydantic import HttpUrl
from fastapi import APIRouter,Depends,status,Response,HTTPException
from sqlalchemy.orm import Session
from .. import schemas,models,utils,config,oAuth
from .. database import get_db 
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags = ["Authenticate"],prefix="/auth")

@router.post("/register", response_model=schemas.GetUser)
def register(credentials : schemas.CreateUser , db : Session = Depends(get_db)):
  existing_user = db.query(models.User).filter(models.User.email == credentials.email).first()
  if existing_user:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists")

  credentials.password = utils.hash_password(credentials.password)
  user = models.User(**credentials.model_dump())
  db.add(user)
  db.commit()
  db.refresh(user)
  if user.role == models.UserRole.STAFF:
        staff_entry = models.Staffs(user_id=user.id, name=user.name)
        db.add(staff_entry)
        db.commit()
  if user.role == models.UserRole.ADMIN:
        admin_entry = models.Admin(user_id=user.id, name=user.name)
        db.add(admin_entry)
        db.commit()
  return user 



@router.post("/login",status_code=status.HTTP_202_ACCEPTED , response_model=schemas.TokenResponse)
def login(credentials:OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
  user = db.query(models.User).filter(models.User.email == credentials.username).first()
  if not user:
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail = "Intended User not Found")
  
  if not utils.verify_password(credentials.password,user.password):
    raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED , detail="Invalid Credentials")

   #creating token
  token = oAuth.create_token(payload={"user_id":user.id})
  return token