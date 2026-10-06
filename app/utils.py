from pwdlib.hashers.bcrypt import BcryptHasher 
from pwdlib.hashers.argon2 import Argon2Hasher 
from pwdlib import PasswordHash

hash_class = PasswordHash([Argon2Hasher(),BcryptHasher()])

def hash_password(password:str) -> str:
    return hash_class.hash(password)

def verify_password(password:str,hashed_password:str) -> bool:
    return hash_class.verify(password,hashed_password)