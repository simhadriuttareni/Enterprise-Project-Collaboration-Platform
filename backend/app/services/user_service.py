from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from ..models.user import User
from ..models.team_member import TeamMember
from ..models.task import Task, TaskStatus
from ..schemas.user import UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        """Update user profile"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def search_users(self, query: str, limit: int = 10, current_user_id: int = None) -> List[User]:
        """Search users by username or email"""
        users = self.db.query(User).filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            ),
            User.is_active == True
        )
        
        if current_user_id:
            users = users.filter(User.id != current_user_id)
        
        return users.limit(limit).all()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        # Get user's projects count
        projects_count = self.db.query(func.count(TeamMember.project_id)).filter(
            TeamMember.user_id == user_id
        ).scalar() or 0
        
        # Get tasks assigned to user
        total_tasks = self.db.query(func.count(Task.id)).filter(
            Task.assignee_id == user_id
        ).scalar() or 0
        
        completed_tasks = self.db.query(func.count(Task.id)).filter(
            Task.assignee_id == user_id,
            Task.status == TaskStatus.DONE
        ).scalar() or 0
        
        overdue_tasks = self.db.query(func.count(Task.id)).filter(
            Task.assignee_id == user_id,
            Task.is_overdue == True,
            Task.status != TaskStatus.DONE
        ).scalar() or 0
        
        return {
            "total_projects": projects_count,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }