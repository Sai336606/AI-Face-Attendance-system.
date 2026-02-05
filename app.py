"""
Face Attendance System - Main Application
With Admin and Student Panel Authentication
"""
import streamlit as st
import sys
sys.path.insert(0, 'C:\\Users\\mohan\\.gemini\\antigravity\\playground\\triple-void')

from db.database import get_database
from auth.session import is_authenticated, get_current_user, is_admin, logout
from db.database_extensions import *

# Page configuration
st.set_page_config(
    page_title="Face Attendance System",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def init_database():
    """Initialize database on app startup"""
    db = get_database()
    # Extend database with new methods
    from db.database_extensions import (
        create_user, get_user_by_username, get_all_users, toggle_user_status,
        get_today_attendance_count, check_attendance_today,
        get_student_attendance_all, get_student_attendance_month,
        get_student_attendance_week, get_student_monthly_attendance_count
    )
    from db.database import Database
    Database.create_user = create_user
    Database.get_user_by_username = get_user_by_username
    Database.get_all_users = get_all_users
    Database.toggle_user_status = toggle_user_status
    Database.get_today_attendance_count = get_today_attendance_count
    Database.check_attendance_today = check_attendance_today
    Database.get_student_attendance_all = get_student_attendance_all
    Database.get_student_attendance_month = get_student_attendance_month
    Database.get_student_attendance_week = get_student_attendance_week
    Database.get_student_monthly_attendance_count = get_student_monthly_attendance_count
    return db

db = init_database()

# Check authentication
if not is_authenticated():
    # Show login page
    from auth import login
    login.show()
else:
    # User is authenticated
    user = get_current_user()
    
    # Sidebar header
    st.sidebar.title(f"Welcome!")
    st.sidebar.subheader(user['name'])
    st.sidebar.caption(f"Role: {user['role'].upper()}")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.sidebar.markdown("---")
    
    # Role-based navigation
    if is_admin():
        # ADMIN PANEL
        st.sidebar.title("Admin Panel")
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "Student Management", "Register Face", "View Logs", "Manage Students"]
        )
        
        # Main header
        st.markdown('<div style="text-align: center;"><h1>🔐 Admin Panel</h1></div>', unsafe_allow_html=True)
        st.markdown("---")
        
        if page == "Dashboard":
            from pages.admin import dashboard
            dashboard.show()
        
        elif page == "Student Management":
            from pages.admin import user_management
            user_management.show()
        
        elif page == "Register Face":
            from pages import register
            register.show()
        
        elif page == "View Logs":
            from pages import logs
            logs.show()
        
        elif page == "Manage Students":
            from pages import manage_students
            manage_students.show()
    
    else:
        # STUDENT PANEL
        st.sidebar.title("Student Panel")
        
        # Check navigation state
        if 'navigate_to' in st.session_state:
            if st.session_state['navigate_to'] == 'mark_attendance':
                page = "Mark Attendance"
                del st.session_state['navigate_to']
            else:
                page = st.sidebar.radio(
                    "Navigation",
                    ["Dashboard", "Mark Attendance", "My Attendance"]
                )
        else:
            page = st.sidebar.radio(
                "Navigation",
                ["Dashboard", "Mark Attendance", "My Attendance"]
            )
        
        # Main header
        st.markdown('<div style="text-align: center;"><h1>👨‍🎓 Student Panel</h1></div>', unsafe_allow_html=True)
        st.markdown("---")
        
        if page == "Dashboard":
            from pages.student import dashboard
            dashboard.show()
        
        elif page == "Mark Attendance":
            from pages.student import mark_attendance
            mark_attendance.show()
        
        elif page == "My Attendance":
            from pages.student import my_attendance
            my_attendance.show()
    
    # System statistics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Stats")
    
    if is_admin():
        student_count = db.get_student_count()
        st.sidebar.metric("Registered Faces", student_count)
        
        today_count = db.get_today_attendance_count()
        st.sidebar.metric("Today's Attendance", today_count)
    else:
        # Student stats
        month_count = db.get_student_monthly_attendance_count(user['student_id'])
        st.sidebar.metric("This Month", f"{month_count} days")
        
        has_marked = db.check_attendance_today(user['student_id'])
        if has_marked:
            st.sidebar.success("✅ Present Today")
        else:
            st.sidebar.warning("❌ Not Marked")
