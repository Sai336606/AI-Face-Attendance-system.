"""
Session Management
Handle user sessions and authentication state
"""
import streamlit as st


def is_authenticated() -> bool:
    """
    Check if user is authenticated
    
    Returns:
        True if authenticated, False otherwise
    """
    return st.session_state.get('authenticated', False)


def get_current_user():
    """
    Get current logged-in user
    
    Returns:
        User dictionary or None
    """
    return st.session_state.get('user', None)


def is_admin() -> bool:
    """
    Check if current user is admin
    Returns:
        True if admin, False otherwise
    """
    user = get_current_user()
    return user and user['role'] == 'admin'


def is_student() -> bool:
    """
    Check if current user is student
    
    Returns:
        True if student, False otherwise
    """
    user = get_current_user()
    return user and user['role'] == 'student'


def logout():
    """Clear session and logout user"""
    st.session_state.clear()
    st.rerun()


def require_auth(role=None):
    """
    Require authentication to access page
    
    Args:
        role: Required role ('admin' or 'student'), None for any authenticated user
    """
    if not is_authenticated():
        st.warning("Please login to access this page")
        st.stop()
    
    if role:
        user = get_current_user()
        if user['role'] != role:
            st.error("Access denied. You don't have permission to view this page.")
            st.stop()
