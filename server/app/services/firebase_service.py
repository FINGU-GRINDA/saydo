import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from config import settings


class FirebaseService:
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            try:
                # Process the private key to ensure newlines are correctly formatted
                private_key = settings.firebase_private_key
                if '\\n' in private_key:
                    private_key = private_key.replace('\\n', '\n')
                
                cred_dict = {
                    "type": "service_account",
                    "project_id": settings.firebase_project_id,
                    "private_key_id": settings.firebase_private_key_id,
                    "private_key": private_key,
                    "client_email": settings.firebase_client_email,
                    "client_id": settings.firebase_client_id,
                    "auth_uri": settings.firebase_auth_uri,
                    "token_uri": settings.firebase_token_uri,
                    "auth_provider_x509_cert_url": settings.firebase_auth_provider_cert_url,
                    "client_x509_cert_url": settings.firebase_client_cert_url
                }
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"Error initializing Firebase Admin SDK: {e}")
        
        self._db = firestore.client()
    
    @property
    def db(self):
        """Get Firestore database instance"""
        if self._db is None:
            self._initialize()
        return self._db
    
    # User operations
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        doc_ref = self.db.collection('users').document(user_data['id'])
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        doc_ref.set(user_data)
        return user_data['id']
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        doc = self.db.collection('users').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        update_data['updated_at'] = datetime.utcnow()
        doc_ref = self.db.collection('users').document(user_id)
        doc_ref.update(update_data)
        return True
    
    # Meeting operations
    async def create_meeting(self, meeting_data: Dict[str, Any]) -> str:
        """Create a new meeting"""
        doc_ref = self.db.collection('meetings').document(meeting_data['id'])
        meeting_data['created_at'] = datetime.utcnow()
        meeting_data['updated_at'] = datetime.utcnow()
        doc_ref.set(meeting_data)
        return meeting_data['id']
    
    async def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        doc = self.db.collection('meetings').document(meeting_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    async def update_meeting(self, meeting_id: str, update_data: Dict[str, Any]) -> bool:
        """Update meeting data"""
        update_data['updated_at'] = datetime.utcnow()
        doc_ref = self.db.collection('meetings').document(meeting_id)
        doc_ref.update(update_data)
        return True
    
    async def get_user_meetings(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get meetings for a user"""
        meetings = (
            self.db.collection('meetings')
            .where('user_id', '==', user_id)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [{'id': doc.id, **doc.to_dict()} for doc in meetings]
    
    async def get_meeting_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by session ID"""
        meetings = (
            self.db.collection('meetings')
            .where('session_id', '==', session_id)
            .limit(1)
            .stream()
        )
        for doc in meetings:
            return {'id': doc.id, **doc.to_dict()}
        return None
    
    async def get_all_meetings(self) -> List[Dict[str, Any]]:
        """Get all meetings (for admin/debugging)"""
        meetings = self.db.collection('meetings').stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in meetings]
    
    # Action operations
    async def create_action(self, action_data: Dict[str, Any]) -> str:
        """Create a new action"""
        doc_ref = self.db.collection('actions').document(action_data['id'])
        action_data['created_at'] = datetime.utcnow()
        action_data['updated_at'] = datetime.utcnow()
        doc_ref.set(action_data)
        return action_data['id']
    
    async def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get action by ID"""
        doc = self.db.collection('actions').document(action_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    async def update_action(self, action_id: str, update_data: Dict[str, Any]) -> bool:
        """Update action data"""
        update_data['updated_at'] = datetime.utcnow()
        doc_ref = self.db.collection('actions').document(action_id)
        doc_ref.update(update_data)
        return True
    
    async def get_meeting_actions(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get actions for a meeting"""
        actions = (
            self.db.collection('actions')
            .where('meeting_id', '==', meeting_id)
            .order_by('created_at')
            .stream()
        )
        return [{'id': doc.id, **doc.to_dict()} for doc in actions]
    
    async def get_pending_actions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending actions for a user"""
        actions = (
            self.db.collection('actions')
            .where('user_id', '==', user_id)
            .where('status', '==', 'pending')
            .order_by('created_at')
            .stream()
        )
        return [{'id': doc.id, **doc.to_dict()} for doc in actions]
    
    # Agent preferences operations
    async def create_agent_preferences(self, prefs_data: Dict[str, Any]) -> str:
        """Create agent preferences"""
        doc_ref = self.db.collection('agent_preferences').document(prefs_data['user_id'])
        prefs_data['created_at'] = datetime.utcnow()
        prefs_data['updated_at'] = datetime.utcnow()
        doc_ref.set(prefs_data)
        return prefs_data['user_id']
    
    async def get_agent_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get agent preferences for user"""
        doc = self.db.collection('agent_preferences').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    async def update_agent_preferences(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update agent preferences"""
        update_data['updated_at'] = datetime.utcnow()
        doc_ref = self.db.collection('agent_preferences').document(user_id)
        doc_ref.update(update_data)
        return True
    
    # Real-time listeners
    def listen_to_meeting_actions(self, meeting_id: str, callback):
        """Listen to real-time updates for meeting actions"""
        def on_snapshot(docs, changes, read_time):
            actions = []
            for doc in docs:
                actions.append({'id': doc.id, **doc.to_dict()})
            callback(actions)
        
        query = (
            self.db.collection('actions')
            .where('meeting_id', '==', meeting_id)
            .order_by('created_at')
        )
        return query.on_snapshot(on_snapshot)
    
    def listen_to_user_meetings(self, user_id: str, callback):
        """Listen to real-time updates for user meetings"""
        def on_snapshot(docs, changes, read_time):
            meetings = []
            for doc in docs:
                meetings.append({'id': doc.id, **doc.to_dict()})
            callback(meetings)
        
        query = (
            self.db.collection('meetings')
            .where('user_id', '==', user_id)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .limit(50)
        )
        return query.on_snapshot(on_snapshot)


# Global Firebase service instance
firebase_service = FirebaseService() 