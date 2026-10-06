from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models,schemas  

class IssueService:
    @staticmethod
    def modify_issue(db: Session, issue_id: int, update_issue:schemas.UpdateIssues,current_user):
        issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
        permitted_for_studs = ["title","description","category","priority"] #
        if not issue:
           raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail = f"Issue with id {issue_id} not found")
        if current_user.role != models.UserRole.ADMIN and current_user.role != models.UserRole.STUDENT:
            raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail = f"User with id {current_user.id} is not authorized to access this issue")
        if current_user.role == models.UserRole.STUDENT and issue.status != models.Status.OPEN:
           raise HTTPException(status_code = status.HTTP_403_FORBIDDEN , detail = "The issue is already on process to be fixed")
    
        updated_data = update_issue.model_dump(exclude_unset = True)

        for key, value in updated_data.items():
           if key not in permitted_for_studs:
               raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You are not permitted to change the {key}")
           else:
               setattr(issue, key, value)
        db.add(issue)
        db.commit()
        db.refresh(issue)
        return issue
issue_serv = IssueService()