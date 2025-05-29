import streamlit as st
from streamlit_extras.colored_header import colored_header
from sqlite_database import create_user, db_connected
from session_state import login_user, toggle_signup_login
from layout import render_custom_button

def render_login_form():
    """Render the login form with modern styling"""
    st.markdown("""
    <div class="form-container">
        <h2 style="color: #325C6A; text-align: center; margin-bottom: 25px;">
            <i class="fas fa-user-circle" style="font-size: 32px; margin-right: 10px; color: #0cb8b6;"></i>
            Login to Your Account
        </h2>
        <p style="text-align: center; margin-bottom: 20px; color: #666;">
            Sign in to access your prediction history and personalized health insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show database status if offline
    if not db_connected:
        st.info("""
        ℹ️ **Running in Offline Mode**
        
        Your database endpoint is currently disabled. You can sign in with demo credentials:
        - Username: **demo**
        - Password: **demo**
        
        Note: In offline mode, your predictions won't be saved to your profile.
        """)
    
    
    # Custom CSS for form elements
    st.markdown("""
    <style>
    div[data-testid="stForm"] {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #0cb8b6 0%, #325C6A 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        width: 100%;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown('<p style="font-weight: 600; color: #325C6A;">Username</p>', unsafe_allow_html=True)
        username = st.text_input("", key="login_username", placeholder="Enter your username")
        
        st.markdown('<p style="font-weight: 600; color: #325C6A;">Password</p>', unsafe_allow_html=True)
        password = st.text_input("", type="password", key="login_password", placeholder="Enter your password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("Sign In")
        
        if submit_button:
            if username and password:
                login_success = login_user(username, password)
                if login_success:
                    st.success("Login successful!")
                    st.rerun()
            else:
                st.warning("Please enter both username and password")
    
    # Display login error message if any
    if st.session_state.login_message:
        st.error(st.session_state.login_message)
    
    # Signup link with custom styling
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <p style="color: #666; margin-bottom: 10px;">Don't have an account?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom button for toggling to signup
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Create an account", use_container_width=True):
            toggle_signup_login()
            st.rerun()

def render_signup_form():
    """Render the signup form with modern styling"""
    st.markdown("""
    <div class="form-container">
        <h2 style="color: #325C6A; text-align: center; margin-bottom: 25px;">
            <i class="fas fa-user-plus" style="font-size: 32px; margin-right: 10px; color: #0cb8b6;"></i>
            Create Your Account
        </h2>
        <p style="text-align: center; margin-bottom: 20px; color: #666;">
            Join CardioPredict to track your health metrics and receive personalized insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if database is available
    if not db_connected:
        st.warning("""
        ⚠️ Database connection is currently unavailable. 
        
        The Neon database endpoint is disabled. New user registration is not available in offline mode.
        
        Please try the demo account with:
        - Username: demo
        - Password: demo
        
        To re-activate the database, visit your Neon dashboard and enable the endpoint.
        """)
        
        # Show login option
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <p style="color: #666; margin-bottom: 10px;">Try our demo account instead</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Login", use_container_width=True):
                st.session_state.show_login = True
                st.session_state.show_signup = False
                st.rerun()
        
        return
    
    # Custom CSS for form elements
    st.markdown("""
    <style>
    div[data-testid="stForm"] {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #0cb8b6 0%, #325C6A 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        width: 100%;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        st.markdown('<p style="font-weight: 600; color: #325C6A;">Username</p>', unsafe_allow_html=True)
        username = st.text_input("", key="signup_username", placeholder="Choose a username")
        
        st.markdown('<p style="font-weight: 600; color: #325C6A;">Email</p>', unsafe_allow_html=True)
        email = st.text_input("", key="signup_email", placeholder="Enter your email address")
        
        st.markdown('<p style="font-weight: 600; color: #325C6A;">Password</p>', unsafe_allow_html=True)
        password = st.text_input("", type="password", key="signup_password", placeholder="Create a password")
        
        st.markdown('<p style="font-weight: 600; color: #325C6A;">Confirm Password</p>', unsafe_allow_html=True)
        confirm_password = st.text_input("", type="password", key="signup_confirm_password", 
                                        placeholder="Confirm your password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button("Create Account")
        
        if submit_button:
            if not (username and email and password and confirm_password):
                st.warning("Please fill all the fields")
            elif password != confirm_password:
                st.warning("Passwords do not match")
            else:
                success, message = create_user(username, email, password)
                
                if success:
                    st.success(message)
                    st.success("Account created successfully! You can now log in.")
                    st.session_state.signup_message = None
                    st.session_state.show_login = True
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error(message)
    
    # Display signup error message if any
    if st.session_state.signup_message:
        st.error(st.session_state.signup_message)
    
    # Login link with custom styling
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <p style="color: #666; margin-bottom: 10px;">Already have an account?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom button for toggling to login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Sign in", use_container_width=True):
            toggle_signup_login()
            st.rerun()

def render_auth_page():
    """Render the authentication page with login or signup form"""
    # Add auth page container styling
    st.markdown("""
    <style>
    .auth-container {
        max-width: 450px;
        margin: 0 auto;
    }
    </style>
    <div class="auth-container">
    """, unsafe_allow_html=True)
    
    if st.session_state.show_login:
        render_login_form()
    else:
        render_signup_form()
        
    st.markdown("</div>", unsafe_allow_html=True)