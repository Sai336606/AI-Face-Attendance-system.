"""
Admin Dashboard
Overview of system statistics and recent activity
"""
import streamlit as st
from db.database import get_database
from auth.session import require_auth
import sys
sys.path.insert(0, 'C:\\Users\\mohan\\.gemini\\antigravity\\playground\\triple-void')
from db.database_extensions import *


def show():
    """Display admin dashboard"""
    require_auth(role='admin')
    
    st.title("📊 Admin Dashboard")
    
    db = get_database()
    
    # Statistics cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_users = len([u for u in db.get_all_users() if u['role'] == 'student'])
        st.metric("Total Students", total_users)
    
    with col2:
        today_count = db.get_today_attendance_count()
        st.metric("Today's Attendance", today_count)
    
    with col3:
        registered_faces = db.get_student_count()
        st.metric("Registered Faces", registered_faces)
    
    st.markdown("---")
    
    # Recent attendance
    st.subheader("Recent Attendance")
    
    recent_logs = db.get_logs(limit=10, status_filter='SUCCESS')
    
    if recent_logs:
        for log in recent_logs:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.text(f"👤 {log['student_id']}")
            
            with col2:
                st.text(f"🕐 {log['timestamp']}")
            
            with col3:
                st.text(f"📊 {log['similarity_score']:.3f}")
    else:
        st.info("No attendance records yet")
    
    # System stats
    st.markdown("---")
    st.subheader("System Statistics")
    
    stats = db.get_log_statistics()
    
    if stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Attempts", stats.get('total_attempts', 0))
        
        with col2:
            st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
        
        with col3:
            st.metric("Avg Processing Time", f"{stats.get('avg_processing_time_ms', 0):.0f} ms")
