"""
Attendance Logs Viewer
Display and analyze attendance records
"""
import streamlit as st
import pandas as pd
from db.database import get_database
from datetime import datetime, timedelta


def show():
    """Display logs page"""
    st.header("Attendance Logs")
    
    db = get_database()
    
    # Statistics section
    st.subheader("Summary Statistics")
    
    stats = db.get_log_statistics()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Attempts", stats.get('total_attempts', 0))
        
        with col2:
            st.metric("Successful", stats.get('successful_attempts', 0))
        
        with col3:
            st.metric("Failed", stats.get('failed_attempts', 0))
        
        with col4:
            success_rate = stats.get('success_rate', 0)
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Average processing time
        avg_time = stats.get('avg_processing_time_ms', 0)
        st.info(f"Average Processing Time: {avg_time:.2f} ms")
    
    else:
        st.info("No attendance records yet.")
        return
    
    st.markdown("---")
    
    # Filters
    st.subheader("Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "SUCCESS", "FAILURE"]
        )
    
    with col2:
        limit = st.number_input(
            "Number of Records",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )
    
    # Fetch logs
    if status_filter == "All":
        logs = db.get_logs(limit=int(limit))
    else:
        logs = db.get_logs(limit=int(limit), status_filter=status_filter)
    
    st.markdown("---")
    
    # Display logs
    st.subheader(f"Attendance Records ({len(logs)} entries)")
    
    if len(logs) == 0:
        st.info("No records found with the selected filters.")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(logs)
    
    # Format columns
    if not df.empty:
        # Rename columns for display
        df_display = df.copy()
        df_display = df_display.rename(columns={
            'log_id': 'ID',
            'student_id': 'Student ID',
            'timestamp': 'Timestamp',
            'status': 'Status',
            'similarity_score': 'Similarity',
            'processing_time_ms': 'Processing Time (ms)'
        })
        
        # Format similarity score
        df_display['Similarity'] = df_display['Similarity'].apply(
            lambda x: f"{x:.4f}" if pd.notna(x) else "N/A"
        )
        
        # Format processing time
        df_display['Processing Time (ms)'] = df_display['Processing Time (ms)'].apply(
            lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
        )
        
        # Color code status
        def highlight_status(row):
            if row['Status'] == 'SUCCESS':
                return ['background-color: #d4edda'] * len(row)
            else:
                return ['background-color: #f8d7da'] * len(row)
        
        # Display table
        st.dataframe(
            df_display,
            hide_index=True
        )
        
        # Download option
        st.markdown("---")
        
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="Download Logs as CSV",
            data=csv,
            file_name=f"attendance_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Detailed view
    st.markdown("---")
    st.subheader("Detailed Records")
    
    for log in logs[:20]:  # Show first 20 in detail
        status_color = "green" if log['status'] == "SUCCESS" else "red"
        status_icon = "[SUCCESS]" if log['status'] == "SUCCESS" else "[FAILED]"
        
        with st.expander(f"{status_icon} {log['timestamp']} - {log['student_id']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Student ID:** {log['student_id']}")
                st.write(f"**Status:** {log['status']}")
                st.write(f"**Timestamp:** {log['timestamp']}")
            
            with col2:
                similarity = log['similarity_score'] if log['similarity_score'] else 0.0
                processing_time = log['processing_time_ms'] if log['processing_time_ms'] else 0.0
                
                st.write(f"**Similarity Score:** {similarity:.4f}")
                st.write(f"**Processing Time:** {processing_time:.2f} ms")
                st.write(f"**Log ID:** {log['log_id']}")
    
    # Performance analysis
    st.markdown("---")
    st.subheader("Performance Analysis")
    
    # Calculate performance metrics
    processing_times = [log['processing_time_ms'] for log in logs if log['processing_time_ms']]
    
    if processing_times:
        avg_time = sum(processing_times) / len(processing_times)
        min_time = min(processing_times)
        max_time = max(processing_times)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Time", f"{avg_time:.2f} ms")
        
        with col2:
            st.metric("Min Time", f"{min_time:.2f} ms")
        
        with col3:
            st.metric("Max Time", f"{max_time:.2f} ms")
        
        # Performance target check
        from utils.config import MAX_PROCESSING_TIME_MS
        
        times_within_target = sum(1 for t in processing_times if t <= MAX_PROCESSING_TIME_MS)
        percentage_within_target = (times_within_target / len(processing_times)) * 100
        
        st.info(f"{percentage_within_target:.1f}% of attempts within target time (<{MAX_PROCESSING_TIME_MS}ms)")
