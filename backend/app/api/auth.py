from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User, AuthProvider
from app.schemas.auth import UserCreate, UserResponse, Token, GoogleAuthRequest
from app.api.dependencies import get_current_user
from app.services.google_auth import get_google_authorization_url, verify_google_token, exchange_code_for_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        auth_provider=AuthProvider.EMAIL
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/google/login")
def google_login():
    """Initiate Google OAuth flow"""
    try:
        authorization_url, state = get_google_authorization_url()
        return {"authorization_url": authorization_url, "state": state}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google OAuth not configured: {str(e)}"
        )


@router.post("/google/callback", response_model=Token)
def google_callback(auth_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for user info
        user_info = exchange_code_for_token(auth_data.code)
        
        # Check if user exists
        user = db.query(User).filter(
            (User.email == user_info['email']) | 
            (User.google_id == user_info['google_id'])
        ).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_info['email'],
                auth_provider=AuthProvider.GOOGLE,
                google_id=user_info['google_id'],
                hashed_password=None  # No password for OAuth users - column is nullable
            )
            db.add(user)
            try:
                db.commit()
                db.refresh(user)
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user: {str(e)}"
                )
        elif user.google_id != user_info['google_id']:
            # Update existing user with Google ID
            user.google_id = user_info['google_id']
            user.auth_provider = AuthProvider.GOOGLE
            db.commit()
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )

