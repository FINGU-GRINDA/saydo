from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.core.auth import create_access_token
from app.services.firebase_service import firebase_service

router = APIRouter(prefix="/demo", tags=["demo"])


class DemoLoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def demo_login(request: DemoLoginRequest):
    """Demo login endpoint that validates against real Firebase user"""
    
    # Check demo credentials
    if request.username != "demo" or request.password != "demo":
        raise HTTPException(status_code=401, detail="Invalid credentials. Use demo/demo")
    
    # Get the demo user from Firebase
    demo_user_id = "demo-user-123"
    user_data = await firebase_service.get_user(demo_user_id)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="Demo user not found. Please run setup_demo_account.py")
    
    # Create JWT token for the demo user
    access_token = create_access_token(data={"sub": demo_user_id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "google_credentials": user_data.get("google_credentials")
        }
    }


@router.get("/status")
async def demo_status():
    """Check if demo account is set up"""
    demo_user_id = "demo-user-123"
    user_data = await firebase_service.get_user(demo_user_id)
    
    return {
        "demo_account_exists": user_data is not None,
        "user_id": demo_user_id,
        "setup_required": user_data is None
    }