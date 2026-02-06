"""
Configuration settings for Face Attendance POC
"""
import os

# Project Root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database Configuration
DB_PATH = os.path.join(PROJECT_ROOT, "attendance.db")

# Face Detection Configuration
MEDIAPIPE_MIN_DETECTION_CONFIDENCE = 0.8
FACE_CROP_PADDING = 20  # pixels to add around detected face

# Face Embedding Configuration
INSIGHTFACE_MODEL_NAME = "buffalo_l"  # Options: buffalo_l, buffalo_s
EMBEDDING_DIM = 512

# Matching Configuration
COSINE_SIMILARITY_THRESHOLD = 0.80  # Increased from 0.65 to prevent false positives
# 0.75 = Good balance, prevents family member confusion
# Lower threshold = more lenient matching (more false positives)
# Higher threshold = stricter matching (more false negatives)

# Liveness Detection Configuration
LIVENESS_FRAMES_COUNT = 3  # Number of consecutive frames to analyze
LIVENESS_MOVEMENT_THRESHOLD = 0.0005  # Lowered for single-frame POC (was 0.002)
EYE_ASPECT_RATIO_THRESHOLD = 0.001  # Lowered for better detection (was 0.15)

# Performance Configuration
MAX_PROCESSING_TIME_MS = 1500  # Maximum allowed processing time (1.5 seconds)
TARGET_SEARCH_TIME_MS = 10  # Target vector search time for 5000 embeddings

# UI Configuration
SUCCESS_COLOR = "green"
FAILURE_COLOR = "red"
WARNING_COLOR = "orange"

# Webcam Configuration
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480
WEBCAM_FPS = 30
