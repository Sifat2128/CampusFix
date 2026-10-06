from typing import Optional, Literal,List, Generic, TypeVar
from pydantic import BaseModel,ConfigDict,EmailStr,Field
from datetime import datetime
from .models import UserRole,Status,Category,Priority

class CreateUser(BaseModel):
    name:str 
    email:EmailStr 
    password:str = Field(min_length=6,max_length=72)
    role:UserRole
    model_config = ConfigDict(from_attributes=True)
    
class GetUser(BaseModel):
    id:int 
    name:str 
    role:UserRole
    created_at:datetime
    model_config = ConfigDict(from_attributes=True)
class TokenId(BaseModel):
    user_id:int 
    model_config = ConfigDict(from_attributes=True)
    
class TokenResponse(BaseModel):
    access_token:str 
    token_type:str 
    model_config = ConfigDict(from_attributes=True)
class UserLogin(BaseModel):
    email:EmailStr
    password:str = Field(min_length=6,max_length=72)
    model_config = ConfigDict(from_attributes=True)

class CreateIssues(BaseModel):
    title:str 
    description:str  
    category:Category=Field(
        description="Category of the issue",
    ) 
    priority:Optional[Priority]=Priority.MEDIUM
    # status:Optional[Literal[Status.OPEN]] = Status.OPEN
    model_config = ConfigDict(from_attributes=True)

class UpdateIssues(BaseModel):
    title:Optional[str] = None
    description:Optional[str] = None
    category:Optional[Category] = None
    priority:Optional[Priority] = None
    model_config = ConfigDict(from_attributes=True)

class GetIssues(BaseModel):
    id:int
    title:str 
    description:str 
    category:Category=Field(
        default=None, 
        description="Category of the issue",
    ) 
    priority:Priority 
    status:Status = Status.OPEN 
    user:str
    assigned_employee:str
    created_at:datetime  
    model_config = ConfigDict(from_attributes=True)
class CreateComment(BaseModel):
    content : str 
    model_config = ConfigDict(from_attributes=True)
class Comments(BaseModel):
    content : str 
    created_at : datetime 
    user_info:GetUser = Field(validation_alias="user_commented")
    model_config = ConfigDict(from_attributes=True)
class CreateVote(BaseModel):
    like : int = 1
    model_config = ConfigDict(from_attributes=True)

class GetVotes(BaseModel):
    user_id : int 
    issue_id: int
    total_votes:int 
    created_at : datetime  
    model_config = ConfigDict(from_attributes = True)


class PaginatedIssues(BaseModel):
    data: List[GetIssues]
    total: int
    skip: int
    limit: int
    model_config = ConfigDict(from_attributes=True)
    

class AuditLog(BaseModel):
    id:int 
    time:datetime 
    issue_id:int 
    user_id:int 
    action:str
    model_config = ConfigDict(from_attributes=True)
    