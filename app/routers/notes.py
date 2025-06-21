from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database.database import get_db
from app.models.note import User, UserPreference
from app.schemas.note import (
    UserCreate, User as UserSchema, Token, Message,
    UserPreferenceCreate, UserPreference as UserPreferenceSchema
)
from app.auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_active_user
)
from app.core.config import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create default user preferences
        user_preference = UserPreference(user_id=db_user.id)
        db.add(user_preference)
        db.commit()
        
        logger.info(f"New user registered: {user.username}")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user


@router.get("/preferences", response_model=UserPreferenceSchema)
def get_user_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    try:
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()
        
        if not preferences:
            # Create default preferences if they don't exist
            preferences = UserPreference(user_id=current_user.id)
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/preferences", response_model=UserPreferenceSchema)
def update_user_preferences(
    preferences_update: UserPreferenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    try:
        preferences = db.query(UserPreference).filter(
            UserPreference.user_id == current_user.id
        ).first()
        
        if not preferences:
            # Create new preferences
            preferences = UserPreference(
                user_id=current_user.id,
                **preferences_update.dict()
            )
            db.add(preferences)
        else:
            # Update existing preferences
            for field, value in preferences_update.dict().items():
                setattr(preferences, field, value)
        
        db.commit()
        db.refresh(preferences)
        
        logger.info(f"User preferences updated: {current_user.username}")
        return preferences
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
