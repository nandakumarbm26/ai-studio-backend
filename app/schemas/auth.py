from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    fname: str
    lname: str
    code: str
    phone: str
    email: EmailStr
    password: str
    role: str = "user"

class UserOut(BaseModel):
    id: int
    fname: str
    lname: str
    code: str
    phone: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True

class Error(BaseModel):
    error: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenRefresh(BaseModel):
    refresh_token: str

