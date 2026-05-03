from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.session import get_db
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse
from ..services.project_service import ProjectService
from ..dependencies.auth import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_active_user)
) -> ProjectResponse:
    """Create new project"""
    service = ProjectService(db)
    return service.create_project(project_in, current_user.id)

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    archived: Optional[bool] = Query(False),
    current_user: User = Depends(get_current_active_user)
) -> List[ProjectResponse]:
    """Get all projects for current user"""
    service = ProjectService(db)
    return service.get_user_projects(current_user.id, skip, limit, archived)

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ProjectDetailResponse:
    """Get project details by ID"""
    service = ProjectService(db)
    project = service.get_project(project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ProjectResponse:
    """Update project"""
    service = ProjectService(db)
    return service.update_project(project_id, project_in, current_user.id)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete project"""
    service = ProjectService(db)
    service.delete_project(project_id, current_user.id)
    return None

@router.post("/{project_id}/members/{user_id}")
async def add_team_member(
    project_id: int,
    user_id: int,
    role: str = Query("member", regex="^(admin|member|viewer)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add member to project"""
    service = ProjectService(db)
    return service.add_team_member(project_id, user_id, role, current_user.id)

@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove member from project"""
    service = ProjectService(db)
    service.remove_team_member(project_id, user_id, current_user.id)
    return None

@router.get("/{project_id}/members")
async def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all members of a project"""
    service = ProjectService(db)
    return service.get_project_members(project_id, current_user.id)