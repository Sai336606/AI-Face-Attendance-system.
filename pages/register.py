"""
Face Registration Page
Capture and store face embeddings with auto-reset
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
from face_engine.detector import FaceDetector
from face_engine.embedder import FaceEmbedder
from db.database import get_database


# Initialize components with caching (module level)
@st.cache_resource
def get_detector():
    return FaceDetector()

@st.cache_resource
def get_embedder():
    return FaceEmbedder()


def show():
    """Display registration page"""
    st.header("Register New Student")
    
    st.markdown("""
    ### Instructions:
    1. Enter student ID and name
    2. Capture a clear face photo using your webcam
    3. Ensure good lighting and look directly at the camera
    4. Only one face should be visible in the frame
    """)
    
    # Get cached components
    detector = get_detector()
    embedder = get_embedder()
    
    db = get_database()
    
    # Initialize session state for form reset
    if 'registration_complete' not in st.session_state:
        st.session_state.registration_complete = False
    
    if 'reset_form' not in st.session_state:
        st.session_state.reset_form = False
    
    # Reset form if registration was completed
    if st.session_state.reset_form:
        st.session_state.reset_form = False
        st.rerun()
    
    # Input fields
    col1, col2 = st.columns(2)
    
    with col1:
        student_id = st.text_input("Student ID", placeholder="e.g., STU001", key="student_id_input")
    
    with col2:
        student_name = st.text_input("Student Name", placeholder="e.g., John Doe", key="student_name_input")
    
    st.markdown("---")
    
    # Camera input
    st.subheader("Capture Face")
    
    camera_image = st.camera_input("Take a photo", key="camera_input")
    
    if camera_image is not None:
        # Convert to OpenCV format
        image = Image.open(camera_image)
        image_np = np.array(image)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        # Display captured image
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Captured Image")
        
        with col2:
            # Process image
            with st.spinner("Processing face..."):
                # Detect face
                result = detector.detect_single_face(image_bgr)
                
                if result is None:
                    st.error("Face Detection Failed")
                    
                    # Check how many faces
                    face_count = detector.detect_faces_count(image_bgr)
                    
                    if face_count == 0:
                        st.warning("No face detected. Please ensure your face is clearly visible.")
                    elif face_count > 1:
                        st.warning(f"Multiple faces detected ({face_count}). Please ensure only one person is in the frame.")
                    
                else:
                    face_crop, detection_info = result
                    
                    # Display detection info
                    st.success(f"Face detected (confidence: {detection_info['confidence']:.2f})")
                    
                    # Show cropped face
                    face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                    st.image(face_rgb, caption="Detected Face")
                    
                    # Generate embedding
                    with st.spinner("Generating face embedding..."):
                        embedding = embedder.generate_embedding(face_crop)
                    
                    if embedding is None:
                        st.error("Embedding Generation Failed")
                        st.warning("Could not generate face embedding. Please try again with a clearer image.")
                    
                    else:
                        st.success(f"Embedding generated ({embedding.shape[0]}-D vector)")
                        
                        # Register button
                        st.markdown("---")
                        
                        if not student_id or not student_name:
                            st.warning("Please enter both Student ID and Name")
                        
                        else:
                            if st.button("Register Student", type="primary"):
                                # Save to database
                                with st.spinner("Saving to database..."):
                                    success = db.insert_student(student_id, student_name, embedding)
                                
                                if success:
                                    st.success(f"Registration Successful: {student_name} ({student_id})")
                                    st.info("Form will reset in 2 seconds for next registration...")
                                    
                                    # Auto-reset after 2 seconds
                                    time.sleep(2)
                                    st.session_state.reset_form = True
                                    st.rerun()
                                
                                else:
                                    st.error("Registration Failed")
                                    st.warning("Could not save to database. Student ID may already exist.")
    
    # Show existing registrations
    st.markdown("---")
    st.subheader("Recently Registered Students")
    
    # Get all students (limited display)
    all_embeddings = db.get_all_embeddings()
    
    if len(all_embeddings) == 0:
        st.info("No students registered yet.")
    else:
        # Display in table format
        recent_students = all_embeddings[-10:]  # Last 10
        
        for student_id, student_name, _ in reversed(recent_students):
            st.text(f"{student_id} - {student_name}")
