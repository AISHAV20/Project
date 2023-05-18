from pydantic import BaseModel
from typing import Optional , Annotated
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email_id: Optional[str] = None
    disabled: Optional[bool] = None

class Register_user(BaseModel):
    username : str
    email_id: str
    password : str
    
class Transaction(BaseModel):
    recipient: str
    amount: float
    
class UserInDB(User):
    hashed_password: str