from sqlalchemy.orm import Session
from sqlalchemy import update
from datetime import datetime
from fastapi import HTTPException, status
from typing import Optional

from ..models.user import User
from ..schemas.auth import UserCreate
from ..core.security import security_manager

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        hashed_password = security_manager.hash_password(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate user by email or username"""
        # Try to find by email first
        user = self.get_user_by_email(username_or_email)
        
        # If not found, try by username
        if not user:
            user = self.get_user_by_username(username_or_email)
        
        # Validate password
        if not user or not security_manager.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated"
            )
        
        return user
    
    def update_last_login(self, user: User) -> None:
        """Update user's last login timestamp"""
        stmt = update(User).where(User.id == user.id).values(last_login=datetime.utcnow())
        self.db.execute(stmt)
        self.db.commit()
    
    def update_password(self, user: User, new_password: str) -> None:
        """Update user's password"""
        hashed_password = security_manager.hash_password(new_password)
        user.hashed_password = hashed_password
        self.db.commit()
    
    def deactivate_user(self, user_id: int) -> None:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            self.db.commit()