from fastapi import FastAPI,HTTPException,status,Depends,Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from . routers import authenticate,issue
from . database import engine,Base
from . import models 
from pydantic import BaseModel
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title = 'CampusFixManagament')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(authenticate.router)
app.include_router(issue.router)

@app.get("/")
def get():
    return {"message":"CampusFix is running"}

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
