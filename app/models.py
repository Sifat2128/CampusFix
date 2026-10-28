from collections import Counter
from sqlalchemy import ColumnElement
from sqlalchemy import null
import enum
from sqlalchemy import Column, String, Integer, Float, TIMESTAMP, Enum, ForeignKey, text,UniqueConstraint,ForeignKeyConstraint,CheckConstraint,Boolean
from sqlalchemy.orm import relationship
from .database import engine, Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"
    ADMIN = "admin"
class Category(str,enum.Enum):
   ELECTRICITY="electricity"
   WATER="water"
   INTERNET="internet"
   CLASSROOM="classroom"
   HOSTEL="hostel"
   CLEANLINESS="cleanliness"
   EQUIPMENT="equipment"
   OTHER="other"
class Priority(str,enum.Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"
    URGENT="urgent"

class Status(str,enum.Enum):
    OPEN="open"
    IN_PROGRESS="in_progress"
    ASSIGNED = "assigned"
    RESOLVED="resolved"
    CLOSED="closed"
    

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False)
    is_verified = Column(Boolean, nullable=False, server_default='false')
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))
    __table_args__ = (
    UniqueConstraint('id', 'role', name='uq_user_id_role'),
    UniqueConstraint('id', 'name', name='uq_user_id_name'),
    )
    issues_posted = relationship("Issue", foreign_keys="[Issue.user_id]", back_populates="poster")
    assigned_issues = relationship("Issue", foreign_keys="[Issue.assigned_employee_id, Issue.assigned_role]", back_populates="assigned_staff")
    staff_user = relationship("Staffs", foreign_keys="[Staffs.user_id, Staffs.name]", back_populates="user_staff")
    commented_issues = relationship("Comments", back_populates="user_commented")
    admin_user = relationship("Admin", foreign_keys="[Admin.user_id, Admin.name]", back_populates="user_admin")
    votes = relationship("Votes",back_populates = "user_vote")
    audit_logs = relationship("AuditLog",back_populates="user_audited")
class Issue(Base):
    __tablename__ = "issue"
    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String,nullable=False)
    description = Column(String,nullable=False)
    category = Column(Enum(Category,name="issue_category"),nullable=False)
    priority = Column(Enum(Priority,name="issue_priority"),nullable=False)
    status = Column(Enum(Status, name="issue_status"), nullable=False, default=Status.OPEN)
    user_id = Column(Integer,ForeignKey("user.id"),nullable=False)
    assigned_employee_id = Column(Integer,nullable=False)
    assigned_role = Column(Enum(UserRole, name="user_role"), default=UserRole.STAFF)
    __table_args__ = (
        ForeignKeyConstraint(
            ['assigned_employee_id', 'assigned_role'],
            ['user.id', 'user.role']
        ),
        CheckConstraint("assigned_role = 'STAFF' ", name="check_staff_role_only"),
    )   
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))
    poster = relationship("User", foreign_keys=[user_id], back_populates="issues_posted")
    assigned_staff = relationship("User", foreign_keys=[assigned_employee_id, assigned_role], back_populates="assigned_issues")
    comments = relationship("Comments", back_populates="issue_commented")
    votes = relationship("Votes",back_populates = "issue_vote")
    @property
    def user(self):
        return self.poster.name if self.poster else None
    @property
    def assigned_employee(self):
        return self.assigned_staff.name if self.assigned_staff else None
    audit_logs = relationship("AuditLog",back_populates="issue_audited")
class Staffs(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer,nullable=False)
    name = Column(String,nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'name'],
            ['user.id', 'user.name'],
            onupdate="CASCADE", ondelete="CASCADE"
        ),
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))
    total_jobs = Column(Integer, nullable=False, server_default=text('0'))
    user_staff = relationship("User", foreign_keys=[user_id, name], back_populates="staff_user")

class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer,nullable=False)
    name = Column(String,nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'name'],
            ['user.id', 'user.name'],
            onupdate="CASCADE", ondelete="CASCADE"
        ),
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('now()'))
    user_admin = relationship("User", foreign_keys=[user_id, name], back_populates="admin_user")
    
class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer,primary_key = True ,nullable = False)
    issue_id = Column(Integer,ForeignKey("issue.id"),nullable = False)
    user_id = Column(Integer,ForeignKey("user.id"),nullable = False)
    content = Column(String,nullable = False)
    created_at = Column(TIMESTAMP,nullable = False,server_default=text("now()"))
    user_commented = relationship("User",foreign_keys=[user_id],back_populates="commented_issues")
    issue_commented = relationship("Issue",foreign_keys=[issue_id],back_populates="comments")
    
class Votes(Base):
    __tablename__ = "votes"
    user_id = Column(Integer,ForeignKey("user.id"),nullable=False , primary_key=True)
    issue_id = Column(Integer,ForeignKey("issue.id"),nullable=False,primary_key=True)
    created_at = Column(TIMESTAMP,nullable=False,server_default=text('now()'))
    user_vote = relationship("User",foreign_keys = [user_id],back_populates = "votes")
    issue_vote = relationship("Issue",foreign_keys = [issue_id],back_populates = "votes") 

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer,primary_key = True , nullable = False , autoincrement=True)
    
    issue_id = Column(Integer,ForeignKey("issue.id"),nullable=False)
    user_id = Column(Integer,ForeignKey("user.id"),nullable=False)
    action = Column(String,nullable = False)
    time = Column(TIMESTAMP,nullable = False , server_default=text('now()'))
    issue_audited = relationship("Issue",foreign_keys=[issue_id],back_populates="audit_logs")
    user_audited = relationship("User",foreign_keys=[user_id],back_populates="audit_logs")
    