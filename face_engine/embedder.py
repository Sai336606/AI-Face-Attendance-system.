"""
Face embedding generator using ONNX models
"""
import cv2
import numpy as np
import onnxruntime as ort
import os
from typing import Optional
from utils.config import EMBEDDING_DIM


class FaceEmbedder:
    """Face embedding generation using ONNX ArcFace model"""
    
    def __init__(self):
        """Initialize ONNX model"""
        self.session = None
        self.input_size = (112, 112)
        
        # Try to load pre-downloaded model
        model_path = self._get_model_path()
        
        if os.path.exists(model_path):
            # Check if file is valid (not corrupted)
            file_size = os.path.getsize(model_path)
            if file_size < 1000:  # File too small, likely corrupted
                print(f"Model file appears corrupted (size: {file_size} bytes), removing...")
                os.remove(model_path)
                print("Please download a valid ArcFace ONNX model manually.")
                print(f"Place it at: {model_path}")
                print("\nRecommended sources:")
                print("  - https://github.com/onnx/models")
                print("  - https://github.com/deepinsight/insightface/tree/master/model_zoo")
                return
            
            try:
                self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
                print(f"ArcFace ONNX model loaded successfully from {model_path}")
            except Exception as e:
                print(f"Error loading ONNX model: {e}")
                print(f"Model file may be corrupted. Removing...")
                try:
                    os.remove(model_path)
                    print(f"Removed corrupted model file.")
                except:
                    pass
                print("\nPlease download a valid ArcFace ONNX model manually.")
                print(f"Place it at: {model_path}")
                print("\nRecommended sources:")
                print("  - https://github.com/onnx/models")
                print("  - https://github.com/deepinsight/insightface/tree/master/model_zoo")
        else:
            print("Model not found!")
            print(f"Please download an ArcFace ONNX model and place it at:")
            print(f"  {model_path}")
            print("\nRecommended sources:")
            print("  - https://github.com/onnx/models")
            print("  - https://github.com/deepinsight/insightface/tree/master/model_zoo")
    
    def _get_model_path(self) -> str:
        """Get path to ONNX model"""
        # Store model in project directory
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        os.makedirs(model_dir, exist_ok=True)
        return os.path.join(model_dir, "arcface_r100.onnx")
    

    
    def generate_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Generate 512-D embedding from face image
        
        Args:
            face_image: Cropped face image (BGR format)
            
        Returns:
            512-D L2-normalized embedding as numpy array
            None if face cannot be processed
        """
        if self.session is None:
            print("Error: Model not loaded. Cannot generate embedding.")
            return None
        
        try:
            # Ensure image is in correct format
            if face_image is None or face_image.size == 0:
                return None
            
            # Preprocess image
            face_preprocessed = self._preprocess_face(face_image)
            
            # Run inference
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: face_preprocessed})
            
            # Get embedding
            embedding = outputs[0].flatten()
            
            # Verify embedding dimension
            if embedding.shape[0] != EMBEDDING_DIM:
                # If model outputs different dimension, pad or truncate
                if embedding.shape[0] < EMBEDDING_DIM:
                    # Pad with zeros
                    embedding = np.pad(embedding, (0, EMBEDDING_DIM - embedding.shape[0]))
                else:
                    # Truncate
                    embedding = embedding[:EMBEDDING_DIM]
            
            # L2 normalize the embedding
            embedding = self._normalize_embedding(embedding)
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def _preprocess_face(self, face_image: np.ndarray) -> np.ndarray:
        """
        Preprocess face image for model input
        
        Args:
            face_image: Input face image (BGR)
            
        Returns:
            Preprocessed image ready for model
        """
        # Resize to model input size
        face_resized = cv2.resize(face_image, self.input_size)
        
        # Convert BGR to RGB
        face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [-1, 1]
        face_normalized = (face_rgb.astype(np.float32) - 127.5) / 127.5
        
        # Transpose to CHW format (channels first)
        face_transposed = np.transpose(face_normalized, (2, 0, 1))
        
        # Add batch dimension
        face_batch = np.expand_dims(face_transposed, axis=0)
        
        return face_batch
    
    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """
        L2 normalize embedding vector
        
        Args:
            embedding: Raw embedding vector
            
        Returns:
            L2-normalized embedding
        """
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension"""
        return EMBEDDING_DIM
    
    def is_ready(self) -> bool:
        """Check if model is loaded and ready"""
        return self.session is not None
