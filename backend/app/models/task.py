from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.base import Base
import enum

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    is_overdue = Column(Boolean, default=False)
    
    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    activities = relationship("ActivityLog", back_populates="task", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_due_date', 'due_date'),
        Index('idx_task_assignee', 'assignee_id'),
        Index('idx_task_project_status', 'project_id', 'status'),
        Index('idx_task_overdue', 'is_overdue', 'status'),
        Index('idx_task_priority', 'priority'),
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"