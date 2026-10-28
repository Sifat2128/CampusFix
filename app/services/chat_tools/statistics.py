from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models

def count_unresolved_issues(db: Session, current_user: models.User) -> int:
    """
    Counts how many issues are currently active/unresolved (OPEN, IN_PROGRESS, ASSIGNED).
    Notice: Uses your synchronous SQLAlchemy Session from database.get_db().
    """
    count = db.query(models.Issue).filter(
        models.Issue.status.in_([
            models.Status.OPEN,
            models.Status.IN_PROGRESS,
            models.Status.ASSIGNED
        ])
    ).count()
    return count

def get_system_statistics(db: Session, current_user: models.User) -> dict:
    """
    Returns high-level statistics across the entire CampusFix platform.
    """
    total = db.query(models.Issue).count()
    open_count = db.query(models.Issue).filter(models.Issue.status == models.Status.OPEN).count()
    in_prog_count = db.query(models.Issue).filter(models.Issue.status == models.Status.IN_PROGRESS).count()
    resolved_count = db.query(models.Issue).filter(models.Issue.status == models.Status.RESOLVED).count()
    closed_count = db.query(models.Issue).filter(models.Issue.status == models.Status.CLOSED).count()

    return {
        "total_issues": total,
        "open_issues": open_count,
        "in_progress_issues": in_prog_count,
        "resolved_issues": resolved_count,
        "closed_issues": closed_count,
        "unresolved_total": open_count + in_prog_count
    }
