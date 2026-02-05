"""
Passive liveness detection
Detects natural micro-movements to prevent spoofing
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional
from utils.config import (
    LIVENESS_FRAMES_COUNT,
    LIVENESS_MOVEMENT_THRESHOLD,
    EYE_ASPECT_RATIO_THRESHOLD
)


class LivenessDetector:
    """Passive liveness detection using MediaPipe landmarks"""
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh for landmark detection"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmark indices (MediaPipe 468 landmarks)
        # Left eye: 33, 160, 158, 133, 153, 144
        # Right eye: 362, 385, 387, 263, 373, 380
        self.LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        
    def check_liveness(self, frames: List[np.ndarray]) -> Tuple[bool, float, str]:
        """
        Check liveness across multiple frames
        
        Args:
            frames: List of consecutive frames (should be LIVENESS_FRAMES_COUNT)
            
        Returns:
            Tuple of (is_live, confidence_score, reason)
        """
        if len(frames) < LIVENESS_FRAMES_COUNT:
            return False, 0.0, "Insufficient frames"
        
        # Extract landmarks from all frames
        landmarks_sequence = []
        for frame in frames:
            landmarks = self._extract_landmarks(frame)
            if landmarks is None:
                return False, 0.0, "Face landmarks not detected"
            landmarks_sequence.append(landmarks)
        
        # Check for micro-movements
        movement_score = self._calculate_movement_variance(landmarks_sequence)
        
        # Check for eye blinks
        blink_detected = self._detect_blink(landmarks_sequence)
        
        # Determine liveness
        is_live = False
        reason = ""
        confidence = 0.0
        
        if movement_score > LIVENESS_MOVEMENT_THRESHOLD:
            is_live = True
            confidence = min(movement_score * 100, 1.0)
            reason = "Natural movement detected"
        elif blink_detected:
            is_live = True
            confidence = 0.8
            reason = "Eye blink detected"
        else:
            is_live = False
            confidence = movement_score * 100
            reason = "Static image detected (no movement)"
        
        return is_live, confidence, reason
    
    def _extract_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract facial landmarks from image
        
        Args:
            image: Input image (BGR)
            
        Returns:
            Numpy array of landmark coordinates (468 x 3)
            None if no face detected
        """
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.face_mesh.process(image_rgb)
        
        if not results.multi_face_landmarks:
            return None
        
        # Get first face landmarks
        face_landmarks = results.multi_face_landmarks[0]
        
        # Convert to numpy array
        landmarks = np.array([[lm.x, lm.y, lm.z] for lm in face_landmarks.landmark])
        
        return landmarks
    
    def _calculate_movement_variance(self, landmarks_sequence: List[np.ndarray]) -> float:
        """
        Calculate variance in landmark positions across frames
        
        Args:
            landmarks_sequence: List of landmark arrays
            
        Returns:
            Movement variance score
        """
        # Stack landmarks into 3D array (frames x landmarks x coordinates)
        landmarks_array = np.array(landmarks_sequence)
        
        # Calculate variance across frames for each landmark
        variance = np.var(landmarks_array, axis=0)
        
        # Average variance across all landmarks and coordinates
        mean_variance = np.mean(variance)
        
        return mean_variance
    
    def _detect_blink(self, landmarks_sequence: List[np.ndarray]) -> bool:
        """
        Detect eye blink in landmark sequence
        
        Args:
            landmarks_sequence: List of landmark arrays
            
        Returns:
            True if blink detected, False otherwise
        """
        ear_values = []
        
        for landmarks in landmarks_sequence:
            # Calculate Eye Aspect Ratio (EAR) for both eyes
            left_ear = self._calculate_ear(landmarks, self.LEFT_EYE_INDICES)
            right_ear = self._calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
            
            # Average EAR
            avg_ear = (left_ear + right_ear) / 2.0
            ear_values.append(avg_ear)
        
        # Check if EAR drops significantly (indicates blink)
        ear_array = np.array(ear_values)
        ear_variance = np.var(ear_array)
        
        # If variance is high, likely a blink occurred
        return ear_variance > EYE_ASPECT_RATIO_THRESHOLD
    
    def _calculate_ear(self, landmarks: np.ndarray, eye_indices: List[int]) -> float:
        """
        Calculate Eye Aspect Ratio (EAR)
        
        Args:
            landmarks: Facial landmarks array
            eye_indices: Indices of eye landmarks
            
        Returns:
            EAR value
        """
        # Get eye landmarks
        eye_points = landmarks[eye_indices]
        
        # Calculate vertical distances
        vertical_1 = np.linalg.norm(eye_points[1] - eye_points[5])
        vertical_2 = np.linalg.norm(eye_points[2] - eye_points[4])
        
        # Calculate horizontal distance
        horizontal = np.linalg.norm(eye_points[0] - eye_points[3])
        
        # EAR formula
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        
        return ear
    
    def close(self):
        """Release resources"""
        if self.face_mesh:
            self.face_mesh.close()
