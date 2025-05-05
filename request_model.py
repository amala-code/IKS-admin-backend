from pydantic import BaseModel, EmailStr

# Login & Signup request model

class User(BaseModel):
    email: EmailStr
    password: str

class UserCreate(User):
    email: EmailStr
    password: str
    phone: str
    fullname: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

