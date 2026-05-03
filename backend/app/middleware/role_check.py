from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..models.team_member import TeamMember, MemberRole
from ..models.project import Project

class RoleCheck:
    """Utility class for role checking"""
    
    @staticmethod
    def is_project_admin(db: Session, project_id: int, user_id: int) -> bool:
        """Check if user is admin of project"""
        team_member = db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.user_id == user_id
        ).first()
        
        return team_member and team_member.role == MemberRole.ADMIN
    
    @staticmethod
    def is_project_member(db: Session, project_id: int, user_id: int) -> bool:
        """Check if user is member of project"""
        team_member = db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.user_id == user_id
        ).first()
        
        return team_member is not None
    
    @staticmethod
    def get_user_role(db: Session, project_id: int, user_id: int) -> Optional[str]:
        """Get user's role in project"""
        team_member = db.query(TeamMember).filter(
            TeamMember.project_id == project_id,
            TeamMember.user_id == user_id
        ).first()
        
        return team_member.role.value if team_member else None
    
    @staticmethod
    def require_project_admin(project_id: int, user_id: int, db: Session):
        """Require project admin access"""
        if not RoleCheck.is_project_admin(db, project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required for this operation"
            )
    
    @staticmethod
    def require_project_access(project_id: int, user_id: int, db: Session):
        """Require project access"""
        if not RoleCheck.is_project_member(db, project_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this project is denied"
            )