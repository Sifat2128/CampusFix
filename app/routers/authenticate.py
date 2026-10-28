from pydantic import HttpUrl
from fastapi import APIRouter,Depends,status,Response,HTTPException,BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .. import schemas,models,utils,config,oAuth,templates
from .. database import get_db 
from fastapi.security import OAuth2PasswordRequestForm
from ..config import settings
from ..security import validate_ruet_email

router = APIRouter(tags = ["Authenticate"],prefix="/auth")

@router.post("/register", response_model=schemas.GetUser)
def register(credentials : schemas.CreateUser, background_tasks: BackgroundTasks, db : Session = Depends(get_db)):
  # Enforce RUET Institutional Email Policy
  validate_ruet_email(credentials.email, credentials.role)

  existing_user = db.query(models.User).filter(models.User.email == credentials.email).first()
  if existing_user:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists")

  credentials.password = utils.hash_password(credentials.password)
  user = models.User(**credentials.model_dump())
  db.add(user)
  db.commit()
  db.refresh(user)
  
  verification_token = oAuth.create_verification_token(user.email)
  background_tasks.add_task(oAuth.send_verification_email, verification_token, user.email)
  
  if user.role == models.UserRole.STAFF:
        staff_entry = models.Staffs(user_id=user.id, name=user.name)
        db.add(staff_entry)
        db.commit()
  if user.role == models.UserRole.ADMIN:
        admin_entry = models.Admin(user_id=user.id, name=user.name)
        db.add(admin_entry)
        db.commit()
  return user 

@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        email = oAuth.verify_verification_email(token)
    except HTTPException:
        html = templates.get_verification_result_page(
            status="error",
            title="Invalid or Expired Link",
            subtitle="The verification token is invalid or has expired.",
            detail="Verification links are time-limited for security. Please request a new link or contact support.",
            button_text="Back to CampusFix",
            redirect_url="/ui"
        )
        return Response(content=html, status_code=status.HTTP_400_BAD_REQUEST, media_type="text/html")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        html = templates.get_verification_result_page(
            status="error",
            title="User Account Not Found",
            subtitle="No CampusFix account is registered with this email.",
            detail="Please check that you entered the right email address or register a new account.",
            button_text="Create an Account",
            redirect_url="/ui"
        )
        return Response(content=html, status_code=status.HTTP_404_NOT_FOUND, media_type="text/html")
    
    if user.is_verified:
        html = templates.get_verification_result_page(
            status="warning",
            title="Already Verified",
            subtitle="Your email address has already been verified.",
            detail="You're all set! You can log in and start reporting and voting on campus issues.",
            button_text="Continue to Log In",
            redirect_url="/ui"
        )
        return Response(content=html, media_type="text/html")
        
    user.is_verified = True
    db.commit()
    html = templates.get_verification_result_page(
        status="success",
        title="Email Verified Successfully!",
        subtitle="Welcome to CampusFix! Your account is active.",
        detail="You can now submit campus maintenance issues, vote on urgent fixes, and track updates in real-time.",
        button_text="Open CampusFix Dashboard",
        redirect_url="/ui"
    )
    return Response(content=html, media_type="text/html")


@router.post("/login",status_code=status.HTTP_202_ACCEPTED , response_model=schemas.TokenResponse)
def login(credentials : schemas.UserLogin , db : Session = Depends(get_db)):
  validate_ruet_email(credentials.email, credentials.role)
  user = db.query(models.User).filter(models.User.email == credentials.email).first()
  if not user:
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail = "Intended User not Found")
  if not utils.verify_password(credentials.password,user.password):
    raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED , detail="Invalid Credentials")
  if not user.is_verified:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Please verify your email before logging in. Check your inbox for the activation link."
    )

  if user.role != credentials.role:
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND , detail = "Invalid Credentials")
   #creating token
  token = oAuth.create_token(payload={"user_id":user.id})
  return token

@router.get("/forget")
@router.get("/reset-password")
def reset_redirect(token: str = ""):
    return RedirectResponse(url=f"/ui?reset_token={token}")

@router.post("/forget")
def forget(email:str ,background_tasks : BackgroundTasks , db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
      return Response(status_code=status.HTTP_200_OK , content = "The user is not found")
    token = oAuth.create_forget_token(email)
    background_tasks.add_task(oAuth.send_forget_token , email , token)
    return {"message" : "Forget Token Sent"}

# @router.post("/verify-forget-token")
# def verify_forget_token(token:str , db:Session = Depends(get_db)):
#   email = oAuth.verify_forget_token(token , db)
#   if not email:
#     raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , detail = "Invalid Token")
#   return {"message" : "Forget Token Verified" , "email" : email}

@router.post("/reset-password",response_model = schemas.GetUser)
def reset_password(token:str , new_password : schemas.ResetPassword , db:Session = Depends(get_db)):
    email = oAuth.verify_forget_token(token )
    if not email:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED , detail = "Invalid Token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND , detail = "User not Found")
    user.password = utils.hash_password(new_password.password)
    db.add(user)
    db.commit()
    return user

@router.post("/resend-verification")
def resend_verification(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email.strip().lower()).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No registered account found with this email.")
    if user.is_verified:
        return {"message": "Your account is already verified! You can log in directly."}
    
    token = oAuth.create_verification_token(user.email)
    background_tasks.add_task(oAuth.send_verification_email, token, user.email)
    return {"message": "A new verification link has been sent to your email. Please check your inbox and spam folder."}

@router.get("/diagnose-email")
async def diagnose_email(to: str = ""):
    target_email = to.strip() or settings.mail_from or settings.admin_one
    info = {
        "mail_server": settings.mail_server,
        "mail_port": settings.mail_port,
        "mail_username": settings.mail_username,
        "mail_from": settings.mail_from,
        "is_password_configured": bool(settings.mail_password and len(settings.mail_password) > 0),
        "target_email": target_email,
    }
    
    if not settings.mail_username or not settings.mail_password:
        return {
            "status": "error",
            "reason": "Missing MAIL_USERNAME or MAIL_PASSWORD in Render Environment Variables",
            "diagnostics": info,
            "solution": "Go to Render Dashboard -> Environment tab and set MAIL_USERNAME and MAIL_PASSWORD (16-character Google App Password)."
        }
        
    try:
        from fastapi_mail import MessageSchema, FastMail
        msg = MessageSchema(
            subject="CampusFix SMTP Diagnostic Test",
            recipients=[target_email],
            body="If you received this message, CampusFix email delivery is working properly on Render!",
            subtype="plain"
        )
        fm = FastMail(utils.get_mail_config())
        await fm.send_message(message=msg)
        return {
            "status": "success",
            "message": f"Diagnostic email successfully delivered to {target_email}!",
            "diagnostics": info
        }
    except Exception as e:
        return {
            "status": "error",
            "exception_type": type(e).__name__,
            "error_detail": str(e),
            "diagnostics": info
        }