import strawberry
from strawberry.types import Info
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core import security
from app.crud.auth import create_user, authenticate_user
from app.core.dependencies import get_current_user
from app.lib.graphql.gql import requires_auth

@strawberry.type
class UserOut:
    id: int
    fname: str
    lname: str
    code: str
    phone: str
    email: str
    role: str

@strawberry.type
class Token:
    access_token: str
    token_type: str
    refresh_token: str

@strawberry.input
class UserCreate:
    fname: str
    lname: str
    code: str
    phone: str
    email: str
    password: str
    role: str = "user"

@strawberry.input
class User:
    id: int
    fname: str
    lname: str
    code: str
    phone: str
    email: str
    role: str

@strawberry.input
class TokenRefreshInput:
    refresh_token: str

@strawberry.type
class AuthMutation:
    
    @strawberry.mutation
    def signup(self, info: Info, user: UserCreate) -> UserOut:
        user = get_current_user(info)
        db: Session = next(get_db())
        try:
            created_user = create_user(db, user)
            return created_user
        except Exception as e:
            return e
    
    @strawberry.mutation
    def login(self, info: Info, email: str, password: str) -> Token:
        db: Session = next(get_db())
        user = authenticate_user(db, email, password)
        if not user:
            raise Exception("Invalid credentials")
        access_token = security.create_access_token(data={"sub": user.email})
        refresh_token = security.create_refresh_token(data={"sub": user.email})
        return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

    @strawberry.mutation
    @requires_auth
    def refresh_token(self, info: Info, payload: TokenRefreshInput) -> Token:
        data = security.decode_refresh_token(payload.refresh_token)
        if not data:
            raise Exception("Invalid refresh token")
        email = data.get("sub")
        access_token = security.create_access_token(data={"sub": email})
        refresh_token = security.create_refresh_token(data={"sub": email})
        return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@strawberry.type
class AuthQuery:
    @strawberry.field
    @requires_auth
    def me(self, info: Info) -> UserOut:
        return get_current_user(info)
