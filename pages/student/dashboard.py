"""
Student Dashboard
Personal overview and quick actions
"""
import streamlit as st
from db.database import get_database
from auth.session import require_auth, get_current_user
import sys
sys.path.insert(0, 'C:\\Users\\mohan\\.gemini\\antigravity\\playground\\triple-void')
from db.database_extensions import *


def show():
    """Display student dashboard"""
    require_auth(role='student')
    
    user = get_current_user()
    
    st.title(f"Welcome, {user['name']}! 👋")
    
    db = get_database()
    
    # Today's status
    has_marked = db.check_attendance_today(user['student_id'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Student ID", user['student_id'])
    
    with col2:
        if has_marked:
            st.success("✅ Present Today")
        else:
            st.warning("❌ Not Marked")
    
    with col3:
        month_count = db.get_student_monthly_attendance_count(user['student_id'])
        st.metric("This Month", f"{month_count} days")
    
    st.markdown("---")
    
    # Quick actions
    if not has_marked:
        st.subheader("Mark Your Attendance")
        st.info("You haven't marked attendance today. Click below to mark now.")
        
        if st.button("📸 Mark Attendance Now", type="primary", use_container_width=True):
            # This will be handled by navigation in main app
            st.session_state['navigate_to'] = 'mark_attendance'
            st.rerun()
    else:
        st.success("✅ You have already marked attendance today!")
        st.info("You can view your attendance history in the 'My Attendance' page.")
    
    # Recent attendance
    st.markdown("---")
    st.subheader("Recent Attendance")
    
    recent = db.get_student_attendance_week(user['student_id'])
    
    if recent:
        for record in recent[:5]:
            date, time, status, score, proc_time = record
            st.text(f"📅 {date} at {time} - Score: {score:.3f}")
    else:
        st.info("No attendance records yet")
