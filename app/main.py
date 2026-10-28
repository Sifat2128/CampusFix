from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import authenticate, issue, chat
from .database import engine, Base
from .config import settings
from .security import SecurityHeadersMiddleware, RateLimiterMiddleware
from . import models 

# Create DB tables if not existing
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[CampusFix Warning] Database table init delayed: {e}")

app = FastAPI(
    title='CampusFix Management API',
    description='Smart Campus Issue Reporting & Resolution Platform with AI Assistant',
    version='2.0.0'
)

# 1. OWASP Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate Limiting Middleware (anti-DDoS & brute force)
app.add_middleware(RateLimiterMiddleware)

# 3. CORS Configuration
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True if origins != ["*"] else False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 4. App Routers
app.include_router(authenticate.router)
app.include_router(issue.router)
app.include_router(chat.router)

@app.get("/")
def get():
    return {
        "message": "CampusFix API is running",
        "docs": "/docs",
        "frontend": "/ui",
        "status": "online"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CampusFix",
        "environment": settings.environment
    }

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
