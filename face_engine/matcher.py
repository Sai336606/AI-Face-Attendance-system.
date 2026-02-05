"""
Cosine similarity-based face matching
Performs 1:N matching against database
"""
import numpy as np
import time
from typing import List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from utils.config import COSINE_SIMILARITY_THRESHOLD


class FaceMatcher:
    """Face matching using cosine similarity"""
    
    def __init__(self, threshold: float = COSINE_SIMILARITY_THRESHOLD):
        """
        Initialize matcher
        
        Args:
            threshold: Minimum similarity score for a match
        """
        self.threshold = threshold
    
    def match_1_to_n(self, query_embedding: np.ndarray, 
                     database_embeddings: List[Tuple[str, str, np.ndarray]]) -> Tuple[Optional[str], Optional[str], float, float]:
        """
        Perform 1:N matching against database
        
        Args:
            query_embedding: Query face embedding (512-D)
            database_embeddings: List of (student_id, student_name, embedding) tuples
            
        Returns:
            Tuple of (student_id, student_name, similarity_score, search_time_ms)
            Returns (None, None, best_score, search_time) if no match above threshold
        """
        if len(database_embeddings) == 0:
            return None, None, 0.0, 0.0
        
        start_time = time.time()
        
        # Extract embeddings and IDs
        student_ids = [item[0] for item in database_embeddings]
        student_names = [item[1] for item in database_embeddings]
        embeddings = np.array([item[2] for item in database_embeddings])
        
        # Reshape query embedding for sklearn
        query_embedding = query_embedding.reshape(1, -1)
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        # Calculate search time
        search_time_ms = (time.time() - start_time) * 1000
        
        # Check if above threshold
        if best_score >= self.threshold:
            return student_ids[best_idx], student_names[best_idx], float(best_score), search_time_ms
        else:
            return None, None, float(best_score), search_time_ms
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0-1)
        """
        embedding1 = embedding1.reshape(1, -1)
        embedding2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        return float(similarity)
    
    def set_threshold(self, threshold: float):
        """Update similarity threshold"""
        self.threshold = threshold
    
    def get_threshold(self) -> float:
        """Get current threshold"""
        return self.threshold
