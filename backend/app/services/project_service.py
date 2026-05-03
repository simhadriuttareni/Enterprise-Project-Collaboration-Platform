from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any

from ..models.project import Project
from ..models.team_member import TeamMember, MemberRole
from ..models.user import User
from ..models.task import Task, TaskStatus
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectDetailResponse
from ..services.activity_service import ActivityService

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_project_access(self, project_id: int, user_id: int) -> bool:
        """Check if user has access to project"""
        team_member = self.db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.user_id == user_id
        ).first()
        return team_member is not None
    
    def check_admin_access(self, project_id: int, user_id: int) -> bool:
        """Check if user is admin of project"""
        team_member = self.db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.user_id == user_id
        ).first()
        return team_member and team_member.role in [MemberRole.ADMIN]
    
    def create_project(self, project_data: ProjectCreate, owner_id: int) -> Project:
        """Create new project"""
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=owner_id
        )
        self.db.add(db_project)
        self.db.flush()  # Get ID without committing
        
        # Auto-add owner as admin team member
        team_member = TeamMember(
            project_id=db_project.id,
            user_id=owner_id,
            role=MemberRole.ADMIN
        )
        self.db.add(team_member)
        
        # Log activity
        activity_service = ActivityService(self.db)
        activity_service.log_activity(
            user_id=owner_id,
            project_id=db_project.id,
            action="created_project",
            details=f"Created project '{db_project.name}'"
        )
        
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def get_user_projects(self, user_id: int, skip: int = 0, limit: int = 100, archived: bool = False) -> List[Project]:
        """Get all projects where user is member"""
        query = self.db.query(Project).join(
            TeamMember, Project.id == TeamMember.project_id
        ).filter(
            TeamMember.user_id == user_id,
            Project.is_archived == archived
        ).order_by(Project.created_at.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_project(self, project_id: int, user_id: int) -> Optional[ProjectDetailResponse]:
        """Get project with stats"""
        if not self.check_project_access(project_id, user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Get project stats
        total_tasks = self.db.query(func.count(Task.id)).filter(Task.project_id == project_id).scalar() or 0
        completed_tasks = self.db.query(func.count(Task.id)).filter(
            Task.project_id == project_id,
            Task.status == TaskStatus.DONE
        ).scalar() or 0
        overdue_tasks = self.db.query(func.count(Task.id)).filter(
            Task.project_id == project_id,
            Task.is_overdue == True,
            Task.status != TaskStatus.DONE
        ).scalar() or 0
        total_members = self.db.query(func.count(TeamMember.id)).filter(
            TeamMember.project_id == project_id
        ).scalar() or 0
        
        return ProjectDetailResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            owner_id=project.owner_id,
            is_archived=project.is_archived,
            created_at=project.created_at,
            updated_at=project.updated_at,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            total_members=total_members
        )
    
    def update_project(self, project_id: int, project_update: ProjectUpdate, user_id: int) -> Project:
        """Update project"""
        if not self.check_admin_access(project_id, user_id):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        self.db.commit()
        self.db.refresh(project)
        
        # Log activity
        activity_service = ActivityService(self.db)
        activity_service.log_activity(
            user_id=user_id,
            project_id=project_id,
            action="updated_project",
            details=f"Updated project '{project.name}'"
        )
        
        return project
    
    def delete_project(self, project_id: int, user_id: int):
        """Delete project"""
        if not self.check_admin_access(project_id, user_id):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        self.db.delete(project)
        self.db.commit()
    
    def add_team_member(self, project_id: int, user_id: int, role: str, admin_id: int) -> Dict[str, Any]:
        """Add member to project"""
        if not self.check_admin_access(project_id, admin_id):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Check if user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already a member
        existing = self.db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.user_id == user_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="User already in project")
        
        member_role = MemberRole(role.lower())
        team_member = TeamMember(
            project_id=project_id,
            user_id=user_id,
            role=member_role
        )
        self.db.add(team_member)
        
        # Log activity
        activity_service = ActivityService(self.db)
        activity_service.log_activity(
            user_id=admin_id,
            project_id=project_id,
            action="added_member",
            details=f"Added user '{user.username}' as {role}"
        )
        
        self.db.commit()
        return {"message": "Member added successfully", "user": user.username}
    
    def remove_team_member(self, project_id: int, user_id: int, admin_id: int):
        """Remove member from project"""
        if not self.check_admin_access(project_id, admin_id):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Cannot remove yourself
        if user_id == admin_id:
            raise HTTPException(status_code=400, detail="Cannot remove yourself")
        
        team_member = self.db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.user_id == user_id
        ).first()
        
        if not team_member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        self.db.delete(team_member)
        self.db.commit()
    
    def get_project_members(self, project_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all project members"""
        if not self.check_project_access(project_id, user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        members = self.db.query(TeamMember, User).join(
            User, TeamMember.user_id == User.id
        ).filter(
            TeamMember.project_id == project_id
        ).all()
        
        return [
            {
                "id": member.TeamMember.id,
                "user_id": member.User.id,
                "username": member.User.username,
                "full_name": member.User.full_name,
                "email": member.User.email,
                "role": member.TeamMember.role.value,
                "joined_at": member.TeamMember.created_at
            }
            for member in members
        ]