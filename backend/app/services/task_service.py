from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models.task import Task, TaskStatus, TaskPriority
from ..models.team_member import TeamMember, MemberRole
from ..models.user import User
from ..schemas.task import TaskCreate, TaskUpdate, TaskFilterParams, TaskResponse
from ..services.activity_service import ActivityService
from ..services.project_service import ProjectService

class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.project_service = ProjectService(db)
    
    def update_overdue_status(self, task_id: int):
        """Update task's overdue status based on due date"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task and task.due_date:
            is_overdue = task.due_date < datetime.now() and task.status != TaskStatus.DONE
            if task.is_overdue != is_overdue:
                task.is_overdue = is_overdue
                self.db.commit()
    
    def create_task(self, task_data: TaskCreate, user_id: int) -> Task:
        """Create new task"""
        # Check project access
        if not self.project_service.check_project_access(task_data.project_id, user_id):
            raise HTTPException(status_code=403, detail="Access denied to this project")
        
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            due_date=task_data.due_date,
            estimated_hours=task_data.estimated_hours,
            project_id=task_data.project_id,
            assignee_id=task_data.assignee_id,
            created_by=user_id
        )
        
        self.db.add(db_task)
        self.db.flush()
        
        # Check overdue status
        self.update_overdue_status(db_task.id)
        
        # Log activity
        activity_service = ActivityService(self.db)
        activity_service.log_activity(
            user_id=user_id,
            project_id=task_data.project_id,
            task_id=db_task.id,
            action="created_task",
            details=f"Created task '{db_task.title}'"
        )
        
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def get_tasks(
        self,
        project_id: int,
        user_id: int,
        filters: TaskFilterParams,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks with filters"""
        if not self.project_service.check_project_access(project_id, user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        query = self.db.query(Task).filter(Task.project_id == project_id)
        
        # Apply filters
        if filters.status:
            query = query.filter(Task.status == filters.status)
        
        if filters.priority:
            query = query.filter(Task.priority == filters.priority)
        
        if filters.assignee_id:
            query = query.filter(Task.assignee_id == filters.assignee_id)
        
        if filters.due_date_from:
            query = query.filter(Task.due_date >= filters.due_date_from)
        
        if filters.due_date_to:
            query = query.filter(Task.due_date <= filters.due_date_to)
        
        if filters.overdue:
            query = query.filter(
                Task.is_overdue == True,
                Task.status != TaskStatus.DONE
            )
        
        if filters.search:
            query = query.filter(
                or_(
                    Task.title.ilike(f"%{filters.search}%"),
                    Task.description.ilike(f"%{filters.search}%")
                )
            )
        
        # Order by priority and due date
        query = query.order_by(
            Task.priority.desc(),
            Task.due_date.asc(),
            Task.created_at.desc()
        )
        
        return query.offset(skip).limit(limit).all()
    
    def get_task(self, task_id: int, user_id: int) -> Task:
        """Get task by ID"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if not self.project_service.check_project_access(task.project_id, user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        self.update_overdue_status(task_id)
        return task
    
    def update_task(self, task_id: int, task_update: TaskUpdate, user_id: int) -> Task:
        """Update task"""
        task = self.get_task(task_id, user_id)
        
        # Check if user has permission to update
        is_admin = self.project_service.check_admin_access(task.project_id, user_id)
        is_creator = task.created_by == user_id
        
        if not (is_admin or is_creator) and task_update.status:
            raise HTTPException(status_code=403, detail="Not authorized to update this task")
        
        update_data = task_update.model_dump(exclude_unset=True)
        old_status = task.status
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        # Handle completion timestamp
        if task.status == TaskStatus.DONE and old_status != TaskStatus.DONE:
            task.completed_at = datetime.now()
        elif task.status != TaskStatus.DONE:
            task.completed_at = None
        
        self.db.flush()
        
        # Update overdue status
        self.update_overdue_status(task_id)
        
        # Log activity
        activity_service = ActivityService(self.db)
        activity_service.log_activity(
            user_id=user_id,
            project_id=task.project_id,
            task_id=task_id,
            action="updated_task",
            details=f"Updated task '{task.title}'"
        )
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def delete_task(self, task_id: int, user_id: int):
        """Delete task"""
        task = self.get_task(task_id, user_id)
        
        # Only admin or task creator can delete
        is_admin = self.project_service.check_admin_access(task.project_id, user_id)
        
        if not (is_admin or task.created_by == user_id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this task")
        
        self.db.delete(task)
        self.db.commit()
    
    def assign_task(self, task_id: int, assignee_id: int, user_id: int) -> Dict[str, Any]:
        """Assign task to a user"""
        task = self.get_task(task_id, user_id)
        
        # Check if assignee is project member
        if not self.project_service.check_project_access(task.project_id, assignee_id):
            raise HTTPException(status_code=400, detail="Assignee must be a project member")
        
        task.assignee_id = assignee_id
        self.db.commit()
        
        # Log activity
        assignee = self.db.query(User).filter(User.id == assignee_id).first()
        activity_service = ActivityService(self.db)
        activity_service.log_activity(
            user_id=user_id,
            project_id=task.project_id,
            task_id=task_id,
            action="assigned_task",
            details=f"Assigned task '{task.title}' to {assignee.username if assignee else 'user'}"
        )
        
        return {"message": "Task assigned successfully"}
    
    def get_overdue_tasks(self, user_id: int) -> List[Task]:
        """Get all overdue tasks for a user"""
        tasks = self.db.query(Task).join(
            TeamMember, Task.project_id == TeamMember.project_id
        ).filter(
            TeamMember.user_id == user_id,
            Task.is_overdue == True,
            Task.status != TaskStatus.DONE
        ).order_by(Task.due_date.asc()).all()
        
        return tasks