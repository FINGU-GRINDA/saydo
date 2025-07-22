from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from typing import Optional
import json
from datetime import datetime
import uuid

from app.services.google_auth import (
    get_authorization_url,
    get_google_auth_flow,
    get_google_user_info
)
from app.services.firebase_service import firebase_service
from app.core.auth import create_access_token, verify_token, get_current_user
from app.models.user import User, UserCreate
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google")
async def google_login():
    authorization_url, state = get_authorization_url()
    return {"authorization_url": authorization_url, "state": state}


@router.get("/google/connect")
async def google_connect(current_user: dict = Depends(get_current_user)):
    """Get Google OAuth URL for connecting services to existing account"""
    authorization_url, state = get_authorization_url()
    
    # Store the current user ID in the state parameter so we know which account to connect to
    import json
    import base64
    
    connect_state = {
        "original_state": state,
        "user_id": current_user["sub"],
        "action": "connect"
    }
    
    encoded_state = base64.b64encode(json.dumps(connect_state).encode()).decode()
    
    # Modify the authorization URL to include our custom state
    modified_url = authorization_url.replace(f"state={state}", f"state={encoded_state}")
    
    return {"authorization_url": modified_url, "state": encoded_state}


@router.get("/google/callback")
async def google_callback(code: str = Query(...), state: Optional[str] = Query(None)):
    try:
        flow = get_google_auth_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        user_info = get_google_user_info(credentials)
        
        # Check if this is a connect flow (linking to existing account)
        connect_info = None
        if state:
            try:
                import json
                import base64
                decoded_state = json.loads(base64.b64decode(state).decode())
                if decoded_state.get("action") == "connect":
                    connect_info = decoded_state
            except:
                pass  # Not a connect flow, proceed with normal login
        
        if connect_info:
            # This is connecting Google to an existing account
            existing_user_id = connect_info["user_id"]
            existing_user = await firebase_service.get_user(existing_user_id)
            
            if not existing_user:
                raise HTTPException(status_code=404, detail="User account not found")
            
            # Update the existing user with Google credentials
            google_tokens = {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "google_user_info": user_info  # Store Google user info for reference
            }
            
            await firebase_service.update_user(existing_user_id, {"google_tokens": google_tokens})
            
            # Redirect back to agent settings with success message
            return RedirectResponse(
                url=f"{settings.frontend_url}/?connected=google&status=success"
            )
        else:
            # This is a regular login flow
            user_id = user_info.get("id")
            user_email = user_info.get("email")
            
            existing_user = await firebase_service.get_user(user_id)
            
            if existing_user:
                # Update existing user
                update_data = {
                    "google_tokens": {
                        "access_token": credentials.token,
                        "refresh_token": credentials.refresh_token,
                        "token_uri": credentials.token_uri,
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "scopes": credentials.scopes
                    }
                }
                await firebase_service.update_user(user_id, update_data)
                user = {**existing_user, **update_data}
            else:
                # Create new user
                user_data = {
                    "id": user_id,
                    "email": user_email,
                    "name": user_info.get("name", ""),
                    "picture": user_info.get("picture"),
                    "google_tokens": {
                        "access_token": credentials.token,
                        "refresh_token": credentials.refresh_token,
                        "token_uri": credentials.token_uri,
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "scopes": credentials.scopes
                    }
                }
                await firebase_service.create_user(user_data)
                user = user_data
            
            # Create JWT token
            access_token = create_access_token(data={"sub": user_id})
            
            # Redirect to frontend with token
            return RedirectResponse(
                url=f"{settings.frontend_url}/auth/callback?token={access_token}"
            )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_current_user(user_id: str = Depends(verify_token)):
    user = await firebase_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove sensitive token data but include connection status
    user_safe = {k: v for k, v in user.items() if k != "google_tokens"}
    
    # Add google_credentials field to indicate if Google is connected
    user_safe["google_credentials"] = bool(user.get("google_tokens"))
    
    return user_safe


@router.post("/disconnect-google")
async def disconnect_google_account(user_id: str = Depends(verify_token)):
    """Disconnect Google account by removing OAuth tokens"""
    try:
        user = await firebase_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove Google tokens
        await firebase_service.update_user(user_id, {
            "google_tokens": None,
            "google_credentials": None
        })
        
        print(f"🔌 Disconnected Google account for user {user_id}")
        
        return {
            "success": True,
            "message": "Google account disconnected successfully"
        }
        
    except Exception as e:
        print(f"Error disconnecting Google account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(user_id: str = Depends(verify_token)):
    # In a real implementation, you might want to invalidate the JWT token
    # For now, just return success
    return {"message": "Logged out successfully"}


# Helper function to get user by ID (used by other modules)
async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID - used by other services"""
    user_data = await firebase_service.get_user(user_id)
    if user_data:
        return User(**user_data)
    return None