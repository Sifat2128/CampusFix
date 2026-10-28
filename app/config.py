import os
from typing import Optional
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: Optional[str] = None
    database_host: Optional[str] = "localhost"
    database_port: Optional[int] = 5432
    database_name: Optional[str] = "campusfix"
    database_username: Optional[str] = "postgres"
    database_password: Optional[str] = ""
    
    secret_key: str = "sasiseait231095abjtgf"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    admin_one: EmailStr = "sifatahasan2108@gmail.com"
    admin_two: EmailStr = "sejutimona2108@gmail.com"
    
    mail_username: Optional[str] = ""
    mail_password: Optional[str] = ""
    mail_from: Optional[str] = ""
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    
    cors_origins: str = "*"
    environment: str = "development"
    app_url: Optional[str] = None
    
    @property
    def base_url(self) -> str:
        if self.app_url:
            return self.app_url.rstrip("/")
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url:
            return render_url.rstrip("/")
        return "http://localhost:8000"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()