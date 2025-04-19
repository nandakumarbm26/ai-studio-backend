from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.auth import UserOut
from app.core.security import decode_access_token
from app.crud import auth as cruds
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(info, db: Session = Depends(get_db)):
    request = info.context["request"]

    # Extract Authorization header
    print(dict(request.headers))
    auth_header = dict(request.headers).get("authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        token = auth_header.split("Bearer ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    # Decode token manually
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Manually open DB session (no Depends in Strawberry)
    db = next(get_db())
    user = cruds.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def get_current_active_user(required_role: str = None):
    def _inner(user: UserOut = Depends(get_current_user)):
        if required_role and user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return user
    return _inner