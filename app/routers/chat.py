from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .. import oAuth, schemas, models
from ..database import get_db
from app.services.chat_service import process_message

router = APIRouter(tags=["Chatbot"], prefix="/chat")

@router.post("/", response_model=schemas.ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: schemas.ChatRequest,
    current_user: models.User = Depends(oAuth.require_verification),
    db: Session = Depends(get_db)
):
    """
    Entry point for the chatbot.
    1. Validates incoming message body via schemas.ChatRequest.
    2. Identifies and verifies the logged-in user via JWT Bearer token.
    3. Injects the database session (db).
    4. Passes everything to process_message() to generate a grounded AI answer.
    """
    result = await process_message(
        db=db,
        message=request.message,
        current_user=current_user
    )
    return result