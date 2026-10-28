from sqlalchemy.orm import Session
from app import models

def get_recent_issues(db: Session, current_user: models.User, limit: int = 5) -> list[dict]:
    """
    Retrieves the most recent campus issues.
    """
    issues = (
        db.query(models.Issue)
        .order_by(models.Issue.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": i.id,
            "title": i.title,
            "category": i.category.value if hasattr(i.category, 'value') else str(i.category),
            "priority": i.priority.value if hasattr(i.priority, 'value') else str(i.priority),
            "status": i.status.value if hasattr(i.status, 'value') else str(i.status),
        }
        for i in issues
    ]

def get_user_reported_issues(db: Session, current_user: models.User) -> list[dict]:
    """
    Retrieves all issues reported by the currently logged-in user.
    """
    issues = (
        db.query(models.Issue)
        .filter(models.Issue.user_id == current_user.id)
        .order_by(models.Issue.created_at.desc())
        .all()
    )
    return [
        {
            "id": i.id,
            "title": i.title,
            "status": i.status.value if hasattr(i.status, 'value') else str(i.status),
            "priority": i.priority.value if hasattr(i.priority, 'value') else str(i.priority),
        }
        for i in issues
    ]

def get_issue_by_id(db: Session, issue_id: int, current_user: models.User) -> dict | None:
    """
    Retrieves details for a specific issue by its ID.
    """
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        return None
    return {
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "category": issue.category.value if hasattr(issue.category, 'value') else str(issue.category),
        "status": issue.status.value if hasattr(issue.status, 'value') else str(issue.status),
        "priority": issue.priority.value if hasattr(issue.priority, 'value') else str(issue.priority),
    }
