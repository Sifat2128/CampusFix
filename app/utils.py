from pwdlib.hashers.bcrypt import BcryptHasher 
from pwdlib.hashers.argon2 import Argon2Hasher 
from pwdlib import PasswordHash
from . import schemas
from . import models
from fastapi_mail import ConnectionConfig
from .config import settings 
hash_class = PasswordHash([Argon2Hasher(),BcryptHasher()])

def hash_password(password:str) -> str:
    return hash_class.hash(password)

def verify_password(password:str,hashed_password:str) -> bool:
    return hash_class.verify(password,hashed_password)

confg = ConnectionConfig(
    mail_username=settings.mail_username,
    mail_password=settings.mail_password,
    mail_from=settings.mail_from,
    mail_port=settings.mail_port,
    mail_server=settings.mail_server,
    mail_starttls=True,
    mail_ssl_tls=False
)