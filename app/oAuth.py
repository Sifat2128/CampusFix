from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException,status,Depends
from sqlalchemy.orm import Session 
from . database import get_db
from . import models,schemas,utils,config 
from .config import settings
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

def require_verification(current_user: models.User = Depends(get_user)):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required to perform this action"
        )
    return current_user


#create function for verification of signing up 

def create_verification_token(email:str , db: Session = Depends(get_db)):
    payload = {"email" : email , "exp" :  datetime.now(UTC)+timedelta(hours = 24) ,"access_type" : "verification"}
    token = jwt.encode(payload , algorithm=ALGORITHM , key = SECRET_KEY)
    return token 

from fastapi_mail import MessageSchema,MessageType,FastMail
from . import templates

async def send_verification_email(token : str , email : str):
    try:
        print(f"[CampusFix Email] Sending verification email to {email}...")
        link = f"{settings.base_url}/auth/verify?token={token}"
        html_body = templates.get_verification_email_html(verification_url=link, email=email)
        
        msg = MessageSchema(
            subject = "Verify your CampusFix account",
            recipients = [email],
            body = html_body,
            subtype = "html"
        )
        fm = FastMail(utils.confg)
        await fm.send_message(message=msg)
        print(f"[CampusFix Email] Successfully sent verification email to {email}")
    except Exception as e:
        print(f"[CampusFix Email Error] Failed sending verification email to {email}: {e}")

#verify the code
def verify_verification_email(token: str):
    try:
        decoded = jwt.decode(token, algorithms=[ALGORITHM], key=SECRET_KEY)
        email = decoded.get("email")
        if decoded.get("access_type") != "verification" or not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
        return email
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")




#creating token and verifying and sending for forgetting email 
def create_forget_token(email:str):
    payload = {"email" : email , "exp" :  datetime.now(UTC)+timedelta(hours = 24) , "type" : "forget"}
    token = jwt.encode(payload , algorithm=ALGORITHM , key = SECRET_KEY)
    return token

async def send_forget_token(email: str , token:str):
    try:
        print(f"[CampusFix Email] Sending password reset email to {email}...")
        link = f"{settings.base_url}/ui?reset_token={token}"
        html_body = templates.get_password_reset_email_html(reset_url=link, email=email)
        
        msg = MessageSchema(
            subject = "Reset your CampusFix password",
            recipients = [email],
            body = html_body,
            subtype = "html"
        )
        fm = FastMail(utils.confg)
        await fm.send_message(message=msg)
        print(f"[CampusFix Email] Successfully sent password reset email to {email}")
    except Exception as e:
        print(f"[CampusFix Email Error] Failed sending password reset email to {email}: {e}")


def verify_forget_token(token : str ):
    try:
        decoded = jwt.decode(token , algorithms=[ALGORITHM] , key = SECRET_KEY)
        email = decoded.get("email")
        type = decoded.get("type")
        if type != "forget":
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED , detail = "Invalid User")
        return email
    except InvalidTokenError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED , detail = "Invalid Token")