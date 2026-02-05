"""
Student Attendance History
View current and previous attendance records
"""
import streamlit as st
import pandas as pd
from db.database import get_database
from auth.session import require_auth, get_current_user
from datetime import datetime
import sys
sys.path.insert(0, 'C:\\Users\\mohan\\.gemini\\antigravity\\playground\\triple-void')
from db.database_extensions import *


def show():
    """Display student attendance history"""
    require_auth(role='student')
    
    user = get_current_user()
    db = get_database()
    
    st.title("📅 My Attendance History")
    
    # Summary statistics
    st.subheader("Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(db.get_student_attendance_all(user['student_id']))
        st.metric("Total Days", total)
    
    with col2:
        month = db.get_student_monthly_attendance_count(user['student_id'])
        st.metric("This Month", month)
    
    with col3:
        week = len(db.get_student_attendance_week(user['student_id']))
        st.metric("This Week", week)
    
    with col4:
        today = "Present" if db.check_attendance_today(user['student_id']) else "Absent"
        if today == "Present":
            st.success(today)
        else:
            st.error(today)
    
    st.markdown("---")
    
    # Filter options
    st.subheader("View Attendance Records")
    
    filter_type = st.selectbox(
        "Select Period",
        ["All Time", "This Month", "This Week"]
    )
    
    # Fetch records based on filter
    if filter_type == "All Time":
        records = db.get_student_attendance_all(user['student_id'])
    elif filter_type == "This Month":
        records = db.get_student_attendance_month(user['student_id'])
    else:  # This Week
        records = db.get_student_attendance_week(user['student_id'])
    
    # Display records
    st.markdown("---")
    
    if len(records) == 0:
        st.info("No attendance records found for the selected period.")
    else:
        st.text(f"Found {len(records)} record(s)")
        
        # Convert to DataFrame
        df = pd.DataFrame(records, columns=[
            'Date', 'Time', 'Status', 'Similarity Score', 'Processing Time (ms)'
        ])
        
        # Format columns
        df['Similarity Score'] = df['Similarity Score'].apply(lambda x: f"{x:.4f}" if x else "N/A")
        df['Processing Time (ms)'] = df['Processing Time (ms)'].apply(lambda x: f"{x:.0f}" if x else "N/A")
        
        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"attendance_{user['student_id']}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
