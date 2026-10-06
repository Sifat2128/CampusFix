from datetime import datetime, UTC
from typing import List, Optional

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas, oAuth
from ..database import get_db
from ..services.issue_service import issue_serv

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post("/create", response_model=schemas.CreateIssues, status_code=status.HTTP_201_CREATED)
def create_issue(issues: schemas.CreateIssues, db: Session = Depends(get_db), current_user=Depends(oAuth.get_user)):
    if current_user.role != models.UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with id {current_user.id} is not a student")
    staff = db.query(models.Staffs).order_by(models.Staffs.total_jobs.asc()).limit(1).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    staff.total_jobs += 1
    db.add(staff)
    db.commit()
    db.refresh(staff)
    issue = models.Issue(**issues.model_dump(exclude={"status"}), user_id=current_user.id,
                         assigned_employee_id=staff.user_id, status=models.Status.OPEN)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    db.add(models.AuditLog(action=f"{current_user.name} created issue", issue_id=issue.id, user_id=current_user.id))
    db.add(models.AuditLog(action=f"Admin assigned issue to Staff #{staff.user_id} ({staff.name})", issue_id=issue.id, user_id=current_user.id))
    db.commit()
    return issue


# NOTE: the list route must come before "/{id}" style routes only if paths clash; "/" and "/{id}" do not.
@router.get("/", response_model=schemas.PaginatedIssues)
def get_issues(
    db: Session = Depends(get_db),
    search: str = "",
    current_user=Depends(oAuth.get_user),
    skip: int = 0,
    limit: int = 10,
    status: Optional[models.Status] = None,
    priority: Optional[models.Priority] = None,
    category: Optional[models.Category] = None,
):
    query = db.query(models.Issue)
    if search:
        query = query.filter(or_(models.Issue.title.ilike(f"%{search}%"),
                                 models.Issue.description.ilike(f"%{search}%")))
    if status is not None:
        query = query.filter(models.Issue.status == status)
    if priority is not None:
        query = query.filter(models.Issue.priority == priority)
    if category is not None:
        query = query.filter(models.Issue.category == category)
    total_count = query.count()
    issues = query.order_by(models.Issue.id.desc()).offset(skip).limit(limit).all()
    return {"data": issues, "total": total_count, "skip": skip, "limit": limit}


@router.get("/{id}", response_model=schemas.GetIssues)
def get_issue(id: int, db: Session = Depends(get_db), current_user=Depends(oAuth.get_user)):
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue with id {id} not found")
    if current_user.role == models.UserRole.STUDENT and issue.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with id {current_user.id} is not authorized to access this issue")
    if current_user.role == models.UserRole.STAFF and issue.assigned_employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with id {current_user.id} is not authorized to access this issue")
    return issue


@router.patch("/{id}", status_code=status.HTTP_200_OK)
def update(id: int, update_issue: schemas.UpdateIssues, db: Session = Depends(get_db), current_user=Depends(oAuth.get_user)):
    return issue_serv.modify_issue(db, id, update_issue, current_user)


@router.post("/{id}/start", status_code=status.HTTP_202_ACCEPTED)
def start_issue(id: int, db: Session = Depends(get_db), current_user=Depends(oAuth.get_user)):
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue with id {id} not found")
    if issue.assigned_employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this issue")
    if issue.status == models.Status.OPEN:
        issue.status = models.Status.IN_PROGRESS
        db.add(models.AuditLog(action=f"Staff #{current_user.id} started work", issue_id=issue.id, user_id=current_user.id))
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.post("/{id}/resolve", status_code=status.HTTP_202_ACCEPTED)
def resolve_issue(id: int, db: Session = Depends(get_db), current_user=Depends(oAuth.get_user)):
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue with id {id} not found")
    if issue.assigned_employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with id {current_user.id} is not authorized to access this issue")
    if issue.status == models.Status.OPEN:
        issue.status = models.Status.IN_PROGRESS
        db.add(models.AuditLog(action=f"Staff #{current_user.id} started work", issue_id=issue.id, user_id=current_user.id))
        db.add(issue)
        db.commit()
        db.refresh(issue)
        return issue
    elif issue.status == models.Status.IN_PROGRESS:
        issue.status = models.Status.RESOLVED
        db.add(models.AuditLog(action=f"Staff #{current_user.id} resolved issue", issue_id=issue.id, user_id=current_user.id))
        db.add(issue)
        db.commit()
        db.refresh(issue)
        staff = db.query(models.Staffs).filter(models.Staffs.user_id == issue.assigned_employee_id).first()
        if staff and staff.total_jobs > 0:
            staff.total_jobs -= 1
            db.add(staff)
            db.commit()
        return issue
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Issue with id {id} is not in progress")


@router.post("/{id}/close", status_code=status.HTTP_202_ACCEPTED)
def close_issue(id: int, db: Session = Depends(get_db), current_user=Depends(oAuth.get_user)):
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue with id {id} not found")
    if current_user.role != models.UserRole.STUDENT or issue.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to close this issue")
    if issue.status != models.Status.RESOLVED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Issue with id {id} is not resolved yet")
    issue.status = models.Status.CLOSED
    db.add(models.AuditLog(action=f"{current_user.name} closed issue", issue_id=issue.id, user_id=current_user.id))
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.post("/{id}/comments", response_model=schemas.Comments)
def add_comment(id: int, comments: schemas.CreateComment, current_user=Depends(oAuth.get_user), db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue with id : {id} was not found")
    allowed_roles = [models.UserRole.STUDENT, models.UserRole.STAFF, models.UserRole.ADMIN]
    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to comment on this issue")
    if issue.user_id != current_user.id and issue.assigned_employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to add comment on this issue")
    comment = models.Comments(**comments.model_dump(), issue_id=issue.id, user_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{id}/comments", response_model=List[schemas.Comments])
def get_comments(id: int, current_user=Depends(oAuth.get_user), db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"issue with id : {id} is not found")
    return (db.query(models.Comments).filter(models.Comments.issue_id == issue.id)
            .order_by(models.Comments.created_at.asc()).all())


@router.get("/{id}/history", response_model=List[schemas.AuditLog])
def get_history(id: int, db: Session = Depends(get_db), current_user=Depends(oAuth.get_user)):
    # FIX: was [ADMIN, STAFF]; students (owner only) and admins may view history.
    permitted_roles = [models.UserRole.ADMIN, models.UserRole.STUDENT]
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue with id : {id} is not found")
    if current_user.role not in permitted_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view history")
    if current_user.role == models.UserRole.STUDENT and issue.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view history")
    return (db.query(models.AuditLog).filter(models.AuditLog.issue_id == issue.id)
            .order_by(models.AuditLog.time.desc()).all())


@router.post("/{id}/vote", response_model=schemas.GetVotes)
def vote(id: int, vote: schemas.CreateVote, current_user=Depends(oAuth.get_user), db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue with id : {id} is not found")
    if current_user.role != models.UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to vote on this issue")

    existing = db.query(models.Votes).filter(models.Votes.issue_id == issue.id,
                                             models.Votes.user_id == current_user.id).first()
    if existing:                       # toggle: vote again to remove your vote
        db.delete(existing)
    else:
        db.add(models.Votes(issue_id=issue.id, user_id=current_user.id))
    db.commit()
    total = db.query(models.Votes).filter(models.Votes.issue_id == issue.id).count()
    return {"user_id": current_user.id, "issue_id": issue.id, "total_votes": total, "created_at": datetime.now(UTC)}


@router.get("/{id}/vote", response_model=schemas.GetVotes)
def voted(id: int, current_user=Depends(oAuth.get_user), db: Session = Depends(get_db)):
    issue = db.query(models.Issue).filter(models.Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Issue with id : {id} is not found")
    if current_user.role != models.UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to vote on this issue")
    # FIX: filter by the current user, and always return the total (even when it is 0)
    mine = db.query(models.Votes).filter(models.Votes.issue_id == issue.id,
                                         models.Votes.user_id == current_user.id).first()
    total = db.query(models.Votes).filter(models.Votes.issue_id == issue.id).count()
    return {"user_id": current_user.id, "issue_id": issue.id, "total_votes": total,
            "created_at": mine.created_at if mine else datetime.now(UTC)}