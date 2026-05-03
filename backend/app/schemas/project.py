from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .user import UserResponse

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_archived: Optional[bool] = None

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProjectDetailResponse(ProjectResponse):
    owner: Optional[UserResponse] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    total_members: int = 0