from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.auth import User
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password

def create_user(db: Session, user: UserCreate):
    # print(db.query(User).all())
    exist_user = db.query(User).filter(User.email == user.email).first()
    
    if exist_user:
        print(exist_user,"print(exist_user)")
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = User(
        fname=user.fname,
        lname=user.lname,
        code=user.code,
        phone=user.phone,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()