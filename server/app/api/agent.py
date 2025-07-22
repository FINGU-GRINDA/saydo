from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime

from app.core.auth import verify_token
from app.services.firebase_service import firebase_service
from app.models.agent_preferences import AgentPreferences, AgentCapability, DEFAULT_CAPABILITIES

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/preferences", response_model=AgentPreferences)
async def get_agent_preferences(user_id: str = Depends(verify_token)):
    """Get user's agent preferences"""
    prefs_data = await firebase_service.get_agent_preferences(user_id)
    
    if not prefs_data:
        # Create default preferences
        default_prefs = {
            "user_id": user_id,
            "capabilities": [cap.dict() for cap in DEFAULT_CAPABILITIES.copy()]
        }
        await firebase_service.create_agent_preferences(default_prefs)
        prefs_data = default_prefs
    
    # Convert capability dictionaries back to AgentCapability objects
    capabilities = []
    for cap_data in prefs_data.get("capabilities", []):
        if isinstance(cap_data, dict):
            capabilities.append(AgentCapability(**cap_data))
        else:
            capabilities.append(cap_data)
    
    # Convert datetime strings back to datetime objects if they exist
    created_at = prefs_data.get('created_at')
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    elif created_at is None:
        created_at = datetime.utcnow()
    
    updated_at = prefs_data.get('updated_at')
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    elif updated_at is None:
        updated_at = datetime.utcnow()
    
    return AgentPreferences(
        user_id=user_id,
        capabilities=capabilities,
        created_at=created_at,
        updated_at=updated_at
    )


@router.put("/preferences", response_model=AgentPreferences)
async def update_agent_preferences(
    preferences_update: Dict[str, Any],
    user_id: str = Depends(verify_token)
):
    """Update user's agent preferences"""
    current_prefs_data = await firebase_service.get_agent_preferences(user_id)
    
    if not current_prefs_data:
        # Create default preferences if they don't exist
        current_prefs_data = {
            "user_id": user_id,
            "capabilities": [cap.dict() for cap in DEFAULT_CAPABILITIES.copy()]
        }
        await firebase_service.create_agent_preferences(current_prefs_data)
    
    # Update capabilities
    if "capabilities" in preferences_update:
        capability_updates = {cap["id"]: cap for cap in preferences_update["capabilities"]}
        
        updated_capabilities = []
        for cap_data in current_prefs_data.get("capabilities", []):
            cap_id = cap_data.get("id") if isinstance(cap_data, dict) else cap_data.id
            
            if cap_id in capability_updates:
                update = capability_updates[cap_id]
                # Update the capability
                if isinstance(cap_data, dict):
                    cap_data["enabled"] = update.get("enabled", cap_data.get("enabled"))
                    if "settings" in update:
                        cap_data["settings"] = update["settings"]
                else:
                    cap_data.enabled = update.get("enabled", cap_data.enabled)
                    if "settings" in update:
                        cap_data.settings = update["settings"]
            
            updated_capabilities.append(cap_data)
        
        # Update in Firebase
        update_data = {
            "capabilities": updated_capabilities
        }
        await firebase_service.update_agent_preferences(user_id, update_data)
        
        # Get updated data
        updated_prefs_data = await firebase_service.get_agent_preferences(user_id)
    else:
        updated_prefs_data = current_prefs_data
    
    # Convert back to AgentPreferences object
    capabilities = []
    for cap_data in updated_prefs_data.get("capabilities", []):
        if isinstance(cap_data, dict):
            capabilities.append(AgentCapability(**cap_data))
        else:
            capabilities.append(cap_data)
    
    # Convert datetime strings back to datetime objects
    created_at = updated_prefs_data.get('created_at')
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    elif created_at is None:
        created_at = datetime.utcnow()
    
    updated_at = updated_prefs_data.get('updated_at')
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    elif updated_at is None:
        updated_at = datetime.utcnow()
    
    return AgentPreferences(
        user_id=user_id,
        capabilities=capabilities,
        created_at=created_at,
        updated_at=updated_at
    )


@router.get("/actions/pending")
async def get_pending_actions(user_id: str = Depends(verify_token)):
    """Get pending actions for the user"""
    actions = await firebase_service.get_pending_actions(user_id)
    return actions


@router.post("/actions/{action_id}/approve")
async def approve_action(
    action_id: str,
    user_id: str = Depends(verify_token)
):
    """Approve and execute an action"""
    # Update action status to approved
    await firebase_service.update_action(action_id, {
        "status": "approved"
    })
    
    return {"message": "Action approved", "action_id": action_id}


@router.post("/actions/{action_id}/reject")
async def reject_action(
    action_id: str,
    user_id: str = Depends(verify_token)
):
    """Reject an action"""
    # Update action status to rejected
    await firebase_service.update_action(action_id, {
        "status": "rejected"
    })
    
    return {"message": "Action rejected", "action_id": action_id}