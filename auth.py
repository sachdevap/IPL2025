import streamlit as st
import json
import os
import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

# Constants
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthManager:
    def __init__(self):
        self.users = {}  # {username: {password_hash: str, role: str}}
        self.load_users()
        
        # Create admin user if not exists
        if not self.get_user("admin"):
            self.create_user("admin", "admin123", "admin")  # Change this password in production!

    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists('data/users.json'):
            with open('data/users.json', 'r') as f:
                self.users = json.load(f)

    def save_users(self):
        """Save users to JSON file"""
        os.makedirs('data', exist_ok=True)
        with open('data/users.json', 'w') as f:
            json.dump(self.users, f)

    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """Create a new user"""
        if username in self.users:
            return False
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.users[username] = {
            "password_hash": password_hash.decode('utf-8'),
            "role": role
        }
        self.save_users()
        return True

    def verify_password(self, username: str, password: str) -> bool:
        """Verify user password"""
        user = self.get_user(username)
        if not user:
            return False
        
        return bcrypt.checkpw(
            password.encode('utf-8'),
            user["password_hash"].encode('utf-8')
        )

    def get_user(self, username: str) -> Optional[dict]:
        """Get user data"""
        return self.users.get(username)

    def create_access_token(self, username: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": username,
            "exp": expire,
            "role": self.users[username]["role"]
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except:
            return None

def init_auth():
    """Initialize authentication manager in session state"""
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()

def login_required(role: Optional[str] = None):
    """Decorator for pages that require authentication"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'token' not in st.session_state:
                st.warning("Please log in to access this page.")
                show_login_page()
                return
            
            user_data = st.session_state.auth_manager.verify_token(st.session_state.token)
            if not user_data:
                st.warning("Your session has expired. Please log in again.")
                show_login_page()
                return
            
            if role and user_data["role"] != role:
                st.error("You don't have permission to access this page.")
                return
            
            func(*args, **kwargs)
        return wrapper
    return decorator

def show_registration_form():
    """Show registration form"""
    with st.form("registration_form"):
        st.subheader("Register New Account")
        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if not new_username or not new_password:
                st.error("Please fill in all fields.")
                return
            
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return
            
            if st.session_state.auth_manager.get_user(new_username):
                st.error("Username already exists. Please choose another.")
                return
            
            if st.session_state.auth_manager.create_user(new_username, new_password):
                st.success("Registration successful! Please log in.")
                return True
            else:
                st.error("Registration failed. Please try again.")
                return False

def show_login_page():
    """Show login form with registration option"""
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted and username and password:
                if st.session_state.auth_manager.verify_password(username, password):
                    token = st.session_state.auth_manager.create_access_token(username)
                    st.session_state.token = token
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        show_registration_form() 