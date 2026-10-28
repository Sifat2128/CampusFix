from sqlalchemy.orm import Session
from app import models
from app.services.ai_provider import ask_ai_with_tools

async def process_message(db: Session, message: str, current_user: models.User) -> dict:
    """
    Coordinates the chatbot request:
    Delegates to the AI Provider using Native LLM Tool Calling.
    The LLM autonomously decides which PostgreSQL tool to call, extracts arguments,
    receives the database result, and synthesizes the final response.
    """
    return await ask_ai_with_tools(
        question=message,
        current_user=current_user,
        db=db
    )
