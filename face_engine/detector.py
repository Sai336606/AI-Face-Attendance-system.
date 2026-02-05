"""
MediaPipe-based face detector
Detects and crops faces from webcam frames
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple
from utils.config import MEDIAPIPE_MIN_DETECTION_CONFIDENCE, FACE_CROP_PADDING


class FaceDetector:
    """Face detection using MediaPipe"""
    
    def __init__(self):
        """Initialize MediaPipe Face Detection"""
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 1 for full range (0-5m), 0 for short range (0-2m)
            min_detection_confidence=MEDIAPIPE_MIN_DETECTION_CONFIDENCE
        )
        
    def detect_single_face(self, image: np.ndarray) -> Optional[Tuple[np.ndarray, dict]]:
        """
        Detect exactly one face in the image
        
        Args:
            image: Input image (BGR format from OpenCV)
            
        Returns:
            Tuple of (cropped_face, detection_info) if exactly one face found
            None if 0 or >1 faces detected
            
            detection_info contains:
                - bbox: (x, y, w, h) bounding box
                - confidence: detection confidence score
        """
        # Convert BGR to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.face_detection.process(image_rgb)
        
        # Check if exactly one face is detected
        if not results.detections or len(results.detections) != 1:
            return None
        
        detection = results.detections[0]
        
        # Get image dimensions
        h, w, _ = image.shape
        
        # Extract bounding box
        bbox = detection.location_data.relative_bounding_box
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        box_w = int(bbox.width * w)
        box_h = int(bbox.height * h)
        
        # Add padding
        x = max(0, x - FACE_CROP_PADDING)
        y = max(0, y - FACE_CROP_PADDING)
        box_w = min(w - x, box_w + 2 * FACE_CROP_PADDING)
        box_h = min(h - y, box_h + 2 * FACE_CROP_PADDING)
        
        # Crop face region
        face_crop = image[y:y+box_h, x:x+box_w]
        
        # Detection info
        detection_info = {
            'bbox': (x, y, box_w, box_h),
            'confidence': detection.score[0]
        }
        
        return face_crop, detection_info
    
    def detect_faces_count(self, image: np.ndarray) -> int:
        """
        Count number of faces in image (for validation)
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Number of faces detected
        """
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(image_rgb)
        
        if not results.detections:
            return 0
        return len(results.detections)
    
    def draw_detection(self, image: np.ndarray, bbox: Tuple[int, int, int, int], 
                      confidence: float, color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Draw bounding box on image for visualization
        
        Args:
            image: Input image
            bbox: Bounding box (x, y, w, h)
            confidence: Detection confidence
            color: Box color (BGR)
            
        Returns:
            Image with drawn bounding box
        """
        x, y, w, h = bbox
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        
        # Draw confidence score
        label = f"Face: {confidence:.2f}"
        cv2.putText(image, label, (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return image
    
    def close(self):
        """Release resources"""
        if self.face_detection:
            self.face_detection.close()
