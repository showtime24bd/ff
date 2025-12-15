
import json
import os
import hashlib
import time
from datetime import datetime, timedelta

class SimpleAuth:
    def __init__(self, db_file='auth_users.json', sessions_file='auth_sessions.json'):
        self.db_file = db_file
        self.sessions_file = sessions_file
        self.users = self.load_users()
        self.sessions = self.load_sessions()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def load_sessions(self):
        """Load sessions from JSON file"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_sessions(self):
        """Save sessions to JSON file"""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def create_session(self, username, hwid):
        """Create persistent session for user - never expires unless manually logged out"""
        session_id = hashlib.sha256(f"{username}:{hwid}:{time.time()}".encode()).hexdigest()
        self.sessions[session_id] = {
            'username': username,
            'hwid': hwid,
            'created_at': datetime.now().isoformat(),
            'never_expires': True  # Session never expires automatically
        }
        self.save_sessions()
        return session_id
    
    def validate_session(self, session_id):
        """Validate if session is still valid - sessions never expire unless manually deleted"""
        if session_id not in self.sessions:
            return False, None
        
        session = self.sessions[session_id]
        return True, session['username']
    
    def delete_session(self, session_id):
        """Delete a session (for logout)"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_sessions()
            return True
        return False
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, hwid=None):
        """Register new user with optional device ID (will be set on first login)"""
        username = username.lower().strip()
        
        # Check if username already exists
        if username in self.users:
            return False, "Username already exists!"
        
        # Create new user (hwid will be set on first login if not provided)
        self.users[username] = {
            'password': self.hash_password(password),
            'device_id': hwid if hwid else None,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'login_count': 0
        }
        
        self.save_users()
        return True, "Registration successful!"
    
    def login(self, username, password, hwid):
        """Login user - auto-register device on first login, then lock to that device"""
        username = username.lower().strip()
        
        # Check if user exists
        if username not in self.users:
            return False, "Invalid username or password!"
        
        user = self.users[username]
        
        # Verify password
        if user['password'] != self.hash_password(password):
            return False, "Invalid username or password!"
        
        # Auto-register device ID on first login
        if user['device_id'] is None:
            user['device_id'] = hwid
            self.save_users()
            print(f"[SimpleAuth] Device ID auto-registered for user: {username}")
        # Check device ID if already registered
        elif user['device_id'] != hwid:
            return False, f"This account is registered on another device! You can only login from your registered device."
        
        # Update login info
        user['last_login'] = datetime.now().isoformat()
        user['login_count'] = user.get('login_count', 0) + 1
        self.save_users()
        
        # Create persistent session
        session_id = self.create_session(username, hwid)
        
        return True, {
            'username': username,
            'subscription': 'active',
            'login_count': user['login_count'],
            'device_id': hwid[:20] + '...',
            'session_id': session_id
        }
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        username = username.lower().strip()
        
        if username not in self.users:
            return False, "User not found!"
        
        user = self.users[username]
        
        # Verify old password
        if user['password'] != self.hash_password(old_password):
            return False, "Invalid old password!"
        
        # Update password
        user['password'] = self.hash_password(new_password)
        self.save_users()
        
        return True, "Password changed successfully!"
    
    def delete_user(self, username, password):
        """Delete user account"""
        username = username.lower().strip()
        
        if username not in self.users:
            return False, "User not found!"
        
        user = self.users[username]
        
        # Verify password
        if user['password'] != self.hash_password(password):
            return False, "Invalid password!"
        
        # Delete user
        del self.users[username]
        self.save_users()
        
        return True, "Account deleted successfully!"
    
    def get_user_info(self, username):
        """Get user information"""
        username = username.lower().strip()
        
        if username not in self.users:
            return None
        
        user = self.users[username]
        device_id = user['device_id']
        device_display = device_id[:20] + '...' if device_id else None
        
        return {
            'username': username,
            'created_at': user['created_at'],
            'last_login': user['last_login'],
            'login_count': user.get('login_count', 0),
            'device_id': device_display
        }
