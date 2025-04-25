from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import UserCreate, UserOut, Token, TokenRefresh, Error
from app.crud.auth import create_user, authenticate_user
from app.core import security
from app.db.session import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.post("/token", response_model=Token)
def login(response:Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(form_data)
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = security.create_access_token(data={"sub": user.email})
    refresh_token = security.create_refresh_token(data={"sub": user.email})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,         # Set to True in prod (needs HTTPS)
        samesite="Lax",      # Or "Strict" or "None" depending on your setup
        max_age=3600,        # 1 hour
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,         # Set to True in prod (needs HTTPS)
        samesite="Lax",      # Or "Strict" or "None" depending on your setup
        max_age=3600,        # 1 hour
        path="/"
    )
    return {"message": "Logged in"}

@router.post("/refresh-token", response_model=Token)
def refresh_token(response:Response, payload: TokenRefresh):
    data = security.decode_refresh_token(payload.refresh_token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    email = data.get("sub")
    access_token = security.create_access_token(data={"sub": email})
    refresh_token = security.create_refresh_token(data={"sub": email})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,         # Set to True in prod (needs HTTPS)
        samesite="Lax",      # Or "Strict" or "None" depending on your setup
        max_age=3600,        # 1 hour
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,         # Set to True in prod (needs HTTPS)
        samesite="Lax",      # Or "Strict" or "None" depending on your setup
        max_age=3600,        # 1 hour
        path="/"
    )
    return {"message": "token refresh success"}