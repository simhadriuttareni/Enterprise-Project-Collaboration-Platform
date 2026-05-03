from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from .....db.session import get_db
from .....schemas.auth import UserCreate, Token, ChangePasswordRequest, RefreshTokenRequest
from .....services.auth_service import AuthService
from .....core.security import security_manager
from .....core.config import settings
from .....dependencies.auth import get_current_active_user
from .....models.user import User

router = APIRouter()

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    request: Request
) -> Any:
    """Register a new user"""
    auth_service = AuthService(db)
    
    # Check if user exists
    existing_user = auth_service.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    existing_username = auth_service.get_user_by_username(user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = auth_service.register_user(user_in)
    
    # Create tokens
    access_token = security_manager.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    refresh_token = security_manager.create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login"""
    auth_service = AuthService(db)
    
    # Authenticate user (email or username)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    auth_service.update_last_login(user)
    
    # Create tokens
    access_token = security_manager.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    refresh_token = security_manager.create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    *,
    db: Session = Depends(get_db),
    refresh_request: RefreshTokenRequest
) -> Any:
    """Refresh access token using refresh token"""
    # Validate refresh token
    payload = security_manager.validate_token_type(refresh_request.refresh_token, "refresh")
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user
    auth_service = AuthService(db)
    user = auth_service.get_user_by_email(email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = security_manager.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    refresh_token = security_manager.create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/change-password")
async def change_password(
    *,
    db: Session = Depends(get_db),
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Change user password"""
    auth_service = AuthService(db)
    
    # Verify old password
    if not security_manager.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Update password
    auth_service.update_password(current_user, password_data.new_password)
    
    return {"message": "Password updated successfully"}

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Logout user (client should discard tokens)"""
    # In a real implementation, you might blacklist the token
    return {"message": "Successfully logged out"}