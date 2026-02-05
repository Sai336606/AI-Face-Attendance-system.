"""
Fully Automatic Blink-Triggered Attendance
Uses continuous video stream with blink detection
No manual buttons - completely hands-free
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
from face_engine.detector import FaceDetector
from face_engine.embedder import FaceEmbedder
from face_engine.liveness import LivenessDetector
from face_engine.matcher import FaceMatcher
from db.database import get_database
from utils.config import MAX_PROCESSING_TIME_MS
import mediapipe as mp


# Initialize components with caching
@st.cache_resource
def get_detector():
    return FaceDetector()

@st.cache_resource
def get_embedder():
    return FaceEmbedder()

@st.cache_resource
def get_liveness_detector():
    return LivenessDetector()

@st.cache_resource
def get_matcher():
    return FaceMatcher()

@st.cache_resource
def get_face_mesh():
    mp_face_mesh = mp.solutions.face_mesh
    return mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )


def calculate_ear(landmarks, eye_indices):
    """Calculate Eye Aspect Ratio"""
    eye_points = np.array([[landmarks[i].x, landmarks[i].y] for i in eye_indices])
    
    vertical_1 = np.linalg.norm(eye_points[1] - eye_points[5])
    vertical_2 = np.linalg.norm(eye_points[2] - eye_points[4])
    horizontal = np.linalg.norm(eye_points[0] - eye_points[3])
    
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear


def detect_blink(image_bgr, face_mesh):
    """Detect eye blink"""
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]
    
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)
    
    if not results.multi_face_landmarks:
        return False, 0.0
    
    landmarks = results.multi_face_landmarks[0].landmark
    
    left_ear = calculate_ear(landmarks, LEFT_EYE)
    right_ear = calculate_ear(landmarks, RIGHT_EYE)
    avg_ear = (left_ear + right_ear) / 2.0
    
    BLINK_THRESHOLD = 0.20
    is_closed = avg_ear < BLINK_THRESHOLD
    
    return is_closed, avg_ear


def process_attendance(frame, detector, embedder, liveness_detector, matcher, db):
    """Process attendance for a captured frame"""
    start_time = time.time()
    
    # Face detection
    result = detector.detect_single_face(frame)
    
    if result is None:
        processing_time = (time.time() - start_time) * 1000
        db.log_attendance(None, "FAILURE", 0.0, processing_time)
        return None, "No face detected"
    
    face_crop, detection_info = result
    
    # Liveness check (optional - can be skipped for speed)
    # Uncomment to enable strict liveness checking
    # frames = [frame, frame, frame]
    # is_live, liveness_score, liveness_reason = liveness_detector.check_liveness(frames)
    
    # Skip liveness for faster processing
    is_live = True
    liveness_reason = "Skipped for speed"
    
    # Generate embedding (fast)
    embedding = embedder.generate_embedding(face_crop)
    
    if embedding is None:
        processing_time = (time.time() - start_time) * 1000
        db.log_attendance(None, "FAILURE", 0.0, processing_time)
        return None, "Embedding generation failed"
    
    # Match
    all_embeddings = db.get_all_embeddings()
    student_id, student_name, similarity_score, search_time = matcher.match_1_to_n(
        embedding, all_embeddings
    )
    
    processing_time = (time.time() - start_time) * 1000
    
    # Log
    if student_id is not None:
        db.log_attendance(student_id, "SUCCESS", similarity_score, processing_time)
    else:
        db.log_attendance(None, "FAILURE", similarity_score, processing_time)
    
    result_data = {
        'student_id': student_id,
        'student_name': student_name,
        'similarity_score': similarity_score,
        'processing_time': processing_time,
        'liveness': liveness_reason,
        'is_live': is_live
    }
    
    return result_data, None


def show():
    """Display fully automatic blink-triggered attendance"""
    st.header("Mark Attendance - Automatic Blink Detection")
    
    st.markdown("""
    ### Fully Automatic - No Buttons!
    1. **Look at camera** - System monitors continuously
    2. **Blink once** - Triggers automatic capture
    3. **Result displays** - Shows for 2 seconds
    4. **Auto-resets** - Ready for next person
    
    **Completely hands-free operation**
    """)
    
    # Get components
    detector = get_detector()
    embedder = get_embedder()
    liveness_detector = get_liveness_detector()
    matcher = get_matcher()
    face_mesh = get_face_mesh()
    db = get_database()
    
    # Check students
    student_count = db.get_student_count()
    
    if student_count == 0:
        st.warning("No students registered yet. Please register faces first.")
        return
    
    st.info(f"Total Registered Students: {student_count}")
    st.markdown("---")
    
    # Initialize session state
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    if 'last_result_time' not in st.session_state:
        st.session_state.last_result_time = 0
    
    if 'result_data' not in st.session_state:
        st.session_state.result_data = None
    
    if 'blink_detected' not in st.session_state:
        st.session_state.blink_detected = False
    
    if 'last_blink_time' not in st.session_state:
        st.session_state.last_blink_time = 0
    
    # Check if should clear result
    current_time = time.time()
    if st.session_state.result_data and (current_time - st.session_state.last_result_time) > 2:
        st.session_state.result_data = None
        st.session_state.processing = False
        st.session_state.blink_detected = False
        st.rerun()
    
    # Status indicator
    status_placeholder = st.empty()
    
    if st.session_state.processing:
        status_placeholder.info("Processing attendance...")
    elif st.session_state.result_data:
        status_placeholder.success("Showing result...")
    else:
        status_placeholder.success("Ready - Blink to capture")
    
    # Video stream section (auto-starts)
    st.subheader("Live Camera Feed")
    
    # Camera runs automatically
    if not st.session_state.processing and st.session_state.result_data is None:
        # Placeholder for video
        video_placeholder = st.empty()
        
        # Open camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("Cannot access camera. Please check permissions.")
            return
        
        # Continuous monitoring
        FRAME_WINDOW = video_placeholder.image([])
        
        while not st.session_state.blink_detected:
            ret, frame = cap.read()
            
            if not ret:
                st.error("Failed to read from camera")
                break
            
            # Detect blink (optimized)
            is_blinking, ear_value = detect_blink(frame, face_mesh)
            
            # Draw on frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Add text overlay
            if is_blinking:
                cv2.putText(frame_rgb, "BLINK DETECTED!", (50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame_rgb, "Blink to capture", (50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.putText(frame_rgb, f"EAR: {ear_value:.3f}", (50, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display frame
            FRAME_WINDOW.image(frame_rgb)
            
            # Check for blink
            current_time = time.time()
            if is_blinking and (current_time - st.session_state.last_blink_time) > 2:
                st.session_state.blink_detected = True
                st.session_state.last_blink_time = current_time
                st.session_state.processing = True
                
                # Process attendance
                result_data, error = process_attendance(
                    frame, detector, embedder, liveness_detector, matcher, db
                )
                
                if error:
                    st.error(error)
                    st.session_state.processing = False
                    st.session_state.blink_detected = False
                    time.sleep(1)
                else:
                    st.session_state.result_data = result_data
                    st.session_state.last_result_time = time.time()
                
                cap.release()
                st.rerun()
                break
            
            time.sleep(0.01)  # ~100 FPS for faster response
        
        cap.release()
    
    # Display result
    if st.session_state.result_data:
        result = st.session_state.result_data
        
        st.markdown("---")
        st.subheader("Attendance Result")
        
        if result['student_id'] is not None:
            st.success("ATTENDANCE MARKED SUCCESSFULLY")
            st.info(f"Match Confidence: {result['similarity_score']:.4f} (Threshold: {matcher.get_threshold()})")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Student", result['student_name'])
                st.metric("ID", result['student_id'])
            with col2:
                st.metric("Similarity", f"{result['similarity_score']:.4f}")
                st.metric("Time", f"{result['processing_time']:.0f} ms")
            
            if result['is_live']:
                st.success(f"Liveness: {result['liveness']}")
            else:
                st.warning(f"Liveness: {result['liveness']}")
        else:
            st.error("IDENTITY NOT RECOGNIZED")
            st.warning(f"Best Score: {result['similarity_score']:.4f} < Threshold: {matcher.get_threshold()}")
            st.info("This face is not registered or similarity too low")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Best Score", f"{result['similarity_score']:.4f}")
            with col2:
                st.metric("Time", f"{result['processing_time']:.0f} ms")
        
        st.info("Resetting in 2 seconds for next person...")
    
    # Recent attendance
    st.markdown("---")
    st.subheader("Recent Attendance")
    
    recent_logs = db.get_logs(limit=5)
    
    if len(recent_logs) == 0:
        st.info("No attendance records yet.")
    else:
        for log in recent_logs:
            status = "✅" if log['status'] == "SUCCESS" else "❌"
            student_info = log['student_id'] if log['student_id'] != 'UNKNOWN' else 'UNKNOWN'
            similarity = log['similarity_score'] if log['similarity_score'] else 0.0
            st.text(f"{status} {log['timestamp']} | {student_info} | Score: {similarity:.3f}")
