from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class user(BaseModel):
    id: int
    username: str
    email: str
    role: str
    class Config:
        from_attributes = True
        
class user_create(BaseModel):
    full_name: Optional[str] = None
    username: str
    email: str
    password: str
    
class user_update(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
 
    
class user_database(user):
    hashed_password: str
    
class token(BaseModel):
    access_token: str
    token_type: str

class token_data(BaseModel):
   username: Optional[str] = None

