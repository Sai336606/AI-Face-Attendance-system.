"""
Student Mark Attendance - Wrapper with Authentication
Adds authentication check and once-per-day restriction
"""
import streamlit as st
import sys
sys.path.insert(0, 'C:\\Users\\mohan\\.gemini\\antigravity\\playground\\triple-void')

from auth.session import require_auth, get_current_user
from db.database import get_database
from db.database_extensions import *

# Import the original attendance module
from pages import attendance as original_attendance


def show():
    """Display mark attendance with authentication and restrictions"""
    # Require student authentication
    require_auth(role='student')
    
    user = get_current_user()
    db = get_database()
    
    st.title("📸 Mark Attendance")
    
    # Check if already marked today
    has_marked = db.check_attendance_today(user['student_id'])
    
    if has_marked:
        st.success("✅ You have already marked attendance today!")
        st.info(f"""
        **Student:** {user['name']}  
        **ID:** {user['student_id']}  
        **Status:** Present
        
        You can only mark attendance once per day.  
        Check 'My Attendance' to view your history.
        """)
        
        # Show recent attendance
        st.markdown("---")
        st.subheader("Your Recent Attendance")
        recent = db.get_student_attendance_week(user['student_id'])
        
        if recent:
            for record in recent[:5]:
                date, time, status, score, proc_time = record
                st.text(f"📅 {date} at {time} - Score: {score:.3f}")
        
        return
    
    # Not marked yet - show attendance marking interface
    st.info(f"Welcome, {user['name']}! Mark your attendance below.")
    st.markdown("---")
    
    # Call original attendance show function
    original_attendance.show()
