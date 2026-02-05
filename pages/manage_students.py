"""
Student Management Page
Edit, delete, and search students
"""
import streamlit as st
import pandas as pd
from db.database import get_database


def show():
    """Display student management page"""
    st.header("Student Management")
    
    db = get_database()
    
    # Get all students
    all_students = db.get_all_embeddings()
    
    if len(all_students) == 0:
        st.info("No students registered yet.")
        return
    
    st.subheader(f"Total Students: {len(all_students)}")
    
    # Search functionality
    st.markdown("---")
    search_term = st.text_input("Search by Student ID or Name", placeholder="Enter search term...")
    
    # Filter students based on search
    if search_term:
        filtered_students = [
            (sid, sname, emb) for sid, sname, emb in all_students
            if search_term.lower() in sid.lower() or search_term.lower() in sname.lower()
        ]
    else:
        filtered_students = all_students
    
    st.markdown("---")
    
    # Display students in a table with actions
    if len(filtered_students) == 0:
        st.warning("No students found matching your search.")
    else:
        st.subheader(f"Showing {len(filtered_students)} student(s)")
        
        # Create DataFrame for display
        df_data = []
        for student_id, student_name, _ in filtered_students:
            df_data.append({
                'Student ID': student_id,
                'Name': student_name
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, hide_index=True)
        
        # Student selection for edit/delete
        st.markdown("---")
        st.subheader("Manage Student")
        
        student_ids = [sid for sid, _, _ in filtered_students]
        selected_id = st.selectbox("Select Student", student_ids)
        
        if selected_id:
            # Get student details
            student_data = next((sid, sname, emb) for sid, sname, emb in filtered_students if sid == selected_id)
            current_id, current_name, current_embedding = student_data
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Edit Student")
                new_name = st.text_input("New Name", value=current_name)
                
                if st.button("Update Name"):
                    if new_name and new_name != current_name:
                        # Update student name
                        success = db.insert_student(current_id, new_name, current_embedding)
                        if success:
                            st.success(f"Updated student name to: {new_name}")
                            st.rerun()
                        else:
                            st.error("Failed to update student")
                    else:
                        st.warning("Please enter a different name")
            
            with col2:
                st.markdown("### Delete Student")
                st.warning(f"Delete {current_name} ({current_id})?")
                
                if st.button("Delete Student", type="primary"):
                    # Delete student
                    try:
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM students WHERE student_id = ?", (current_id,))
                        conn.commit()
                        st.success(f"Deleted student: {current_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete student: {e}")
