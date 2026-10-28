from sqlalchemy.orm import Session
from app import models

def get_issue_audit_history(db: Session, issue_id: int, current_user: models.User, limit: int = 10) -> list[dict]:
    """
    Retrieves the historical timeline of changes (status changes, assignments) for an issue.
    """
    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.issue_id == issue_id)
        .order_by(models.AuditLog.time.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "event_id": log.id,
            "action": log.action,
            "timestamp": log.time.isoformat() if log.time else None,
            "user_id": log.user_id,
        }
        for log in logs
    ]
