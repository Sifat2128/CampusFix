from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException,status,Depends
from sqlalchemy.orm import Session 
from . database import get_db
from . import models,schemas,utils,config 
from datetime import datetime,timedelta,UTC
import jwt 
from jwt import InvalidTokenError
oAuthScheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

ALGORITHM = config.settings.algorithm 
ACCESS_TIME = config.settings.access_token_expire_minutes
SECRET_KEY = config.settings.secret_key

def create_token(payload:dict,time_access_expire: None | timedelta = None):
    token = payload.copy()
    if time_access_expire:
        expire = datetime.now(UTC)+time_access_expire
    else:
        expire = datetime.now(UTC)+timedelta(minutes=ACCESS_TIME)
    token.update({"exp" : expire})
    encoded_token = jwt.encode(payload = token , key = SECRET_KEY , algorithm=ALGORITHM)
    return {"access_token":encoded_token, "token_type":"Bearer"}


def verify_token(token:str , credentials_error:HTTPException):
    try:

        decoded = jwt.decode(token,key = SECRET_KEY,algorithms=[ALGORITHM])
        user_id = decoded.get("user_id")
        if not user_id:
           raise credentials_error 
        token = schemas.TokenId(user_id=user_id)
    except InvalidTokenError:
        raise credentials_error
    return token
    
def get_user(db:Session = Depends(get_db),token : str = Depends(oAuthScheme)):
    
    credenials_error = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED)
    token_id = verify_token(token,credenials_error)
    user_id = token_id.user_id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user