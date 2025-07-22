from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_tokens: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class UserInDB(User):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_tokens: Optional[Dict[str, Any]] = None