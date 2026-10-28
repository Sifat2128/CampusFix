from pwdlib.hashers.bcrypt import BcryptHasher 
from pwdlib.hashers.argon2 import Argon2Hasher 
from pwdlib import PasswordHash
from fastapi_mail import ConnectionConfig
from .config import settings 

hash_class = PasswordHash([Argon2Hasher(), BcryptHasher()])

def hash_password(password: str) -> str:
    return hash_class.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_class.verify(password, hashed_password)

def get_mail_config() -> ConnectionConfig:
    """Safely builds mail config ensuring valid email addresses even if env vars are partial."""
    sender = settings.mail_from or settings.mail_username or "sifatahasan2108@gmail.com"
    username = settings.mail_username or "sifatahasan2108@gmail.com"
    password = settings.mail_password or ""
    
    return ConnectionConfig(
        mail_username=username,
        mail_password=password,
        mail_from=sender,
        mail_port=settings.mail_port or 587,
        mail_server=settings.mail_server or "smtp.gmail.com",
        mail_starttls=True,
        mail_ssl_tls=False
    )

confg = get_mail_config()