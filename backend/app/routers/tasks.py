from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.session import get_db
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskFilterParams
from ..services.task_service import TaskService
from ..dependencies.auth import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(get_current_active_user)
) -> TaskResponse:
    """Create new task"""
    service = TaskService(db)
    return service.create_task(task_in, current_user.id)

@router.get("/project/{project_id}", response_model=List[TaskResponse])
async def get_tasks(
    project_id: int,
    status: Optional[str] = Query(None, regex="^(todo|in_progress|review|done)$"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high|urgent)$"),
    assignee_id: Optional[int] = Query(None),
    overdue: Optional[bool] = Query(False),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[TaskResponse]:
    """Get tasks for a project with filters"""
    service = TaskService(db)
    
    filters = TaskFilterParams(
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        overdue=overdue,
        search=search
    )
    
    return service.get_tasks(project_id, current_user.id, filters, skip, limit)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> TaskResponse:
    """Get task by ID"""
    service = TaskService(db)
    return service.get_task(task_id, current_user.id)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> TaskResponse:
    """Update task"""
    service = TaskService(db)
    return service.update_task(task_id, task_in, current_user.id)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete task"""
    service = TaskService(db)
    service.delete_task(task_id, current_user.id)
    return None

@router.get("/dashboard/overdue")
async def get_overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all overdue tasks for current user"""
    service = TaskService(db)
    return service.get_overdue_tasks(current_user.id)

@router.post("/{task_id}/assign/{user_id}")
async def assign_task(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign task to user"""
    service = TaskService(db)
    return service.assign_task(task_id, user_id, current_user.id)