"""
Admin User Management
Create and manage student accounts
"""
import streamlit as st
from db.database import get_database
from utils.auth_utils import hash_password
from auth.session import require_auth
import sys
sys.path.insert(0, 'C:\\Users\\mohan\\.gemini\\antigravity\\playground\\triple-void')
from db.database_extensions import *


def show():
    """Display user management page"""
    require_auth(role='admin')
    
    st.title("👥 Student Management")
    
    db = get_database()
    
    tab1, tab2 = st.tabs(["Create Student", "Manage Students"])
    
    with tab1:
        st.subheader("Create New Student Account")
        
        with st.form("create_student_form"):
            student_id = st.text_input("Student ID", placeholder="e.g., STU001")
            name = st.text_input("Full Name", placeholder="e.g., John Doe")
            username = st.text_input("Username", placeholder="e.g., john.doe")
            password = st.text_input("Password", type="password", placeholder="Minimum 6 characters")
            
            submitted = st.form_submit_button("Create Student", type="primary")
            
            if submitted:
                if not all([student_id, name, username, password]):
                    st.error("All fields are required")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    # Check if username already exists
                    existing = db.get_user_by_username(username)
                    if existing:
                        st.error(f"Username '{username}' already exists")
                    else:
                        password_hash = hash_password(password)
                        user_id = db.create_user(student_id, name, username, password_hash, 'student')
                        
                        if user_id:
                            st.success(f"✅ Student created successfully!")
                            st.info(f"""
                            **Login Credentials:**  
                            Username: `{username}`  
                            Password: `{password}`  
                            
                            Please share these credentials with the student.
                            """)
                        else:
                            st.error("Failed to create student. Student ID might already exist.")
    
    with tab2:
        st.subheader("All Students")
        
        users = db.get_all_users()
        students = [u for u in users if u['role'] == 'student']
        
        if not students:
            st.info("No students created yet")
        else:
            st.text(f"Total Students: {len(students)}")
            st.markdown("---")
            
            for student in students:
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.text(f"🆔 {student['student_id']}")
                    st.caption(student['name'])
                
                with col2:
                    st.text(f"👤 @{student['username']}")
                
                with col3:
                    if student['is_active']:
                        st.success("Active")
                    else:
                        st.error("Disabled")
                
                with col4:
                    button_label = "Disable" if student['is_active'] else "Enable"
                    if st.button(button_label, key=f"toggle_{student['id']}"):
                        new_status = not student['is_active']
                        if db.toggle_user_status(student['id'], new_status):
                            st.success(f"Student {button_label.lower()}d")
                            st.rerun()
                        else:
                            st.error("Failed to update status")
                
                st.markdown("---")
