from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import RefreshTokenModel, UserModel
from app.schemas import AccessTokenResponse, RefreshTokenRequest, TokenResponse, UserCreate, UserLogin, UserResponse
from app.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    hash_token,
    utc_now,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = UserModel(email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    refresh_token = create_refresh_token()
    db.add(
        RefreshTokenModel(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=utc_now() + timedelta(days=settings.refresh_token_expire_days),
        )
    )
    db.commit()

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    refresh_token = create_refresh_token()
    db.add(
        RefreshTokenModel(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=utc_now() + timedelta(days=settings.refresh_token_expire_days),
        )
    )
    db.commit()

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_access_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    stored_token = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.token_hash == hash_token(payload.refresh_token))
        .first()
    )

    if not stored_token or stored_token.revoked or stored_token.expires_at < utc_now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    return AccessTokenResponse(access_token=create_access_token(stored_token.user_id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    stored_token = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.token_hash == hash_token(payload.refresh_token))
        .first()
    )

    if stored_token:
        stored_token.revoked = True
        db.commit()

    return None


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
