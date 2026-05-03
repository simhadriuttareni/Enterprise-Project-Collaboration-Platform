from sqlalchemy import Column, Integer, ForeignKey, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from ..db.base import Base
import enum

class MemberRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="team_members")
    user = relationship("User", back_populates="team_memberships")
    
    # Unique constraint to prevent duplicate members
    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', name='unique_project_member'),
        Index('idx_team_project', 'project_id'),
        Index('idx_team_user', 'user_id'),
        Index('idx_team_role', 'role'),
    )
    
    def __repr__(self):
        return f"<TeamMember(project_id={self.project_id}, user_id={self.user_id}, role={self.role})>"