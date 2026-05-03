from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..db.session import get_db
from ..schemas.user import UserResponse, UserUpdate
from ..services.user_service import UserService
from ..dependencies.auth import get_current_active_user
from ..models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Get current user info"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Update current user"""
    service = UserService(db)
    return service.update_user(current_user.id, user_in)

@router.get("/search", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[UserResponse]:
    """Search for users by username or email"""
    service = UserService(db)
    return service.search_users(q, limit, current_user.id)

@router.get("/projects/stats")
async def get_user_projects_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's projects statistics"""
    service = UserService(db)
    return service.get_user_stats(current_user.id)