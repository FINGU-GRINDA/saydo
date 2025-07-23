#!/usr/bin/env python3

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import sys
import os

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from config.settings import settings

def setup_demo_account():
    """Create a demo account in Firebase"""
    
    print("🔥 Initializing Firebase...")
    
    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        cred_dict = {
            "type": "service_account",
            "project_id": settings.firebase_project_id,
            "private_key_id": settings.firebase_private_key_id,
            "private_key": settings.firebase_private_key,
            "client_email": settings.firebase_client_email,
            "client_id": settings.firebase_client_id,
            "auth_uri": settings.firebase_auth_uri,
            "token_uri": settings.firebase_token_uri,
            "auth_provider_x509_cert_url": settings.firebase_auth_provider_cert_url,
            "client_x509_cert_url": settings.firebase_client_cert_url
        }
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # Demo user data
    demo_user_id = "demo-user-123"
    demo_user_data = {
        "id": demo_user_id,
        "email": "demo@rindacallops.com",
        "name": "Demo User",
        "picture": "https://ui-avatars.com/api/?name=Demo+User&background=3B82F6&color=fff",
        "google_credentials": None,  # Will be set when user connects Google OAuth
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    print("👤 Creating demo user...")
    
    # Create or update demo user
    user_ref = db.collection('users').document(demo_user_id)
    user_ref.set(demo_user_data)
    
    print(f"✅ Demo user created: {demo_user_data['email']}")
    
    # Create default agent preferences for demo user
    print("🤖 Setting up default agent preferences...")
    
    default_capabilities = [
        {
            "id": "summary",
            "name": "Generate Summary",
            "description": "Create a concise summary of any conversation.",
            "enabled": True,
            "requires_google_auth": False,
            "settings": {}
        },
        {
            "id": "todo",
            "name": "Extract Action Items", 
            "description": "Pull out clear, actionable tasks from a conversation.",
            "enabled": True,
            "requires_google_auth": False,
            "settings": {}
        },
        {
            "id": "email",
            "name": "Draft Follow-up Email",
            "description": "Write a draft email based on the conversation.",
            "enabled": True,
            "requires_google_auth": True,
            "settings": {}
        },
        {
            "id": "calendar",
            "name": "Schedule Meeting",
            "description": "Identify and suggest meeting times with participants.",
            "enabled": True,
            "requires_google_auth": True,
            "settings": {
                "default_duration": 60,
                "reminder_minutes": 15
            }
        },
        {
            "id": "sheets",
            "name": "Create Project Task",
            "description": "Add a new task to a project board like Trello or Asana.",
            "enabled": False,
            "requires_google_auth": True,
            "settings": {}
        },
        {
            "id": "slack",
            "name": "Share to Slack",
            "description": "Send key summaries or updates to a Slack channel.",
            "enabled": False,
            "requires_google_auth": False,
            "settings": {}
        },
        {
            "id": "crm",
            "name": "Update CRM Contact",
            "description": "Automatically update contact records with conversation notes.",
            "enabled": False,
            "requires_google_auth": False,
            "settings": {}
        },
        {
            "id": "analytics",
            "name": "Log Sales Activity",
            "description": "Track call outcomes and update sales pipeline.",
            "enabled": False,
            "requires_google_auth": False,
            "settings": {}
        }
    ]
    
    agent_prefs_data = {
        "user_id": demo_user_id,
        "capabilities": default_capabilities,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    prefs_ref = db.collection('agent_preferences').document(demo_user_id)
    prefs_ref.set(agent_prefs_data)
    
    print("✅ Agent preferences created")
    
    print("\n🎉 Demo account setup complete!")
    print("📧 Email: demo@rindacallops.com")
    print("🔑 Login: demo/demo")
    print("👤 User ID: demo-user-123")
    print("\n🔗 Next steps:")
    print("1. Login with demo/demo")
    print("2. Go to Agent Settings")
    print("3. Connect Google OAuth for calendar and email capabilities")
    print("\nThe demo account is now ready to use with real Google integrations!")

if __name__ == "__main__":
    try:
        setup_demo_account()
    except Exception as e:
        print(f"❌ Error setting up demo account: {e}")
        sys.exit(1) 