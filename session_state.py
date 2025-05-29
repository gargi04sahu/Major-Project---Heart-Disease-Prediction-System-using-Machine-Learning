import streamlit as st
from sqlite_database import authenticate_user, get_user_by_id, db_connected

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True
    
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    
    if 'login_message' not in st.session_state:
        st.session_state.login_message = None
    
    if 'signup_message' not in st.session_state:
        st.session_state.signup_message = None

def login_user(username, password):
    """Try to log in a user and set session state accordingly"""
    success, user_id, is_admin = authenticate_user(username, password)
    
    if success:
        user = get_user_by_id(user_id)
        st.session_state.user_id = user_id
        
        # Handle both regular User object and dictionary (for offline mode)
        if isinstance(user, dict):
            st.session_state.username = user.get('username', 'Guest')
            st.session_state.is_admin = user.get('is_admin', False)
        else:
            st.session_state.username = user.username
            st.session_state.is_admin = getattr(user, 'is_admin', False)
            
        st.session_state.is_authenticated = True
        st.session_state.login_message = None
        
        # Show database status warning if needed
        if not db_connected:
            st.warning("Running in offline mode. Your activities won't be saved. Please reactivate your database endpoint.")
            
        return True
    else:
        st.session_state.login_message = "Invalid username or password"
        return False

def logout_user():
    """Log out the current user"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_authenticated = False
    st.session_state.is_admin = False
    st.session_state.show_login = True
    st.session_state.show_signup = False

def is_authenticated():
    """Check if the user is authenticated"""
    return st.session_state.is_authenticated

def is_admin():
    """Check if the current user is an administrator"""
    return st.session_state.is_admin

def get_current_user_id():
    """Get the current user's ID"""
    return st.session_state.user_id

def get_current_username():
    """Get the current user's username"""
    return st.session_state.username

def toggle_signup_login():
    """Toggle between signup and login forms"""
    st.session_state.show_login = not st.session_state.show_login
    st.session_state.show_signup = not st.session_state.show_signup
    st.session_state.login_message = None
    st.session_state.signup_message = None