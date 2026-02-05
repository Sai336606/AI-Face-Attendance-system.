"""
Login Page
User authentication interface
"""
import streamlit as st
from db.database import get_database
from utils.auth_utils import verify_password, generate_session_id


def show():
    """Display login page"""
    # Note: set_page_config is called in app.py, not here
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("Face Attendance System")
        st.markdown("### Login")
        
        # Login form
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                # Authenticate user
                db = get_database()
                user = db.get_user_by_username(username)
                
                if user and verify_password(password, user['password']):
                    # Check if account is active
                    if user['is_active']:
                        # Create session
                        session_id = generate_session_id()
                        
                        # Store in session state
                        st.session_state['authenticated'] = True
                        st.session_state['user'] = user
                        st.session_state['session_id'] = session_id
                        
                        st.success(f"Welcome, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Your account has been disabled. Please contact administrator.")
                else:
                    st.error("Invalid username or password")
        
        # Info box
        st.markdown("---")
        st.info("""
        **Default Admin Credentials:**  
        Username: `admin`  
        Password: `admin123`
        
        **Students:** Use credentials provided by admin
        """)
