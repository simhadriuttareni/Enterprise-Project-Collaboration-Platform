from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from fastapi import HTTPException, status

from ..models.activity_log import ActivityLog
from ..models.team_member import TeamMember

class ActivityService:
    def __init__(self, db: Session):
        self.db = db
    
    def log_activity(
        self,
        user_id: int,
        action: str,
        project_id: Optional[int] = None,
        task_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLog:
        """Log user activity"""
        activity = ActivityLog(
            user_id=user_id,
            project_id=project_id,
            task_id=task_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def get_project_activities(
        self,
        project_id: int,
        user_id: int,
        limit: int = 50,
        skip: int = 0
    ) -> List[ActivityLog]:
        """Get activities for a project"""
        # Check if user has access to project
        team_member = self.db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.user_id == user_id
        ).first()
        
        if not team_member:
            raise HTTPException(status_code=403, detail="Access denied")
        
        activities = self.db.query(ActivityLog).filter(
            ActivityLog.project_id == project_id
        ).order_by(
            desc(ActivityLog.created_at)
        ).offset(skip).limit(limit).all()
        
        return activities
    
    def get_user_activities(
        self,
        user_id: int,
        limit: int = 50,
        skip: int = 0
    ) -> List[ActivityLog]:
        """Get activities for a specific user"""
        activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).order_by(
            desc(ActivityLog.created_at)
        ).offset(skip).limit(limit).all()
        
        return activities
    
    def get_task_activities(
        self,
        task_id: int,
        user_id: int,
        limit: int = 50
    ) -> List[ActivityLog]:
        """Get activities for a task"""
        activities = self.db.query(ActivityLog).filter(
            ActivityLog.task_id == task_id
        ).order_by(
            desc(ActivityLog.created_at)
        ).limit(limit).all()
        
        return activities