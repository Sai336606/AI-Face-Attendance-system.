"""
Database operations for Face Attendance POC
Handles all SQLite interactions
"""
import sqlite3
import pickle
import numpy as np
from datetime import datetime
from typing import List, Tuple, Optional, Dict
from utils.config import DB_PATH
from db.models import (
    CREATE_STUDENTS_TABLE,
    CREATE_ATTENDANCE_LOGS_TABLE,
    CREATE_LOGS_INDEX,
    CREATE_LOGS_STATUS_INDEX
)


class Database:
    """Handles all database operations for the attendance system"""
    
    def __init__(self, db_path: str = DB_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        
    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute(CREATE_STUDENTS_TABLE)
        cursor.execute(CREATE_ATTENDANCE_LOGS_TABLE)
        cursor.execute(CREATE_LOGS_INDEX)
        cursor.execute(CREATE_LOGS_STATUS_INDEX)
        
        # Create users table for authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'student')),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print(f"Database initialized at {self.db_path}")
    
    def insert_student(self, student_id: str, student_name: str, embedding: np.ndarray) -> bool:
        """
        Insert or update student embedding
        
        Args:
            student_id: Unique student identifier
            student_name: Student's name
            embedding: Face embedding (512-D numpy array)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Serialize embedding
            embedding_blob = pickle.dumps(embedding)
            
            # Insert or replace (allows overwrite for demo)
            cursor.execute("""
                INSERT OR REPLACE INTO students (student_id, student_name, embedding, created_at)
                VALUES (?, ?, ?, ?)
            """, (student_id, student_name, embedding_blob, datetime.now()))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error inserting student: {e}")
            return False
    
    def get_all_embeddings(self) -> List[Tuple[str, str, np.ndarray]]:
        """
        Retrieve all student embeddings for matching
        
        Returns:
            List of tuples: (student_id, student_name, embedding)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT student_id, student_name, embedding FROM students")
            rows = cursor.fetchall()
            
            # Deserialize embeddings
            results = []
            for row in rows:
                student_id = row['student_id']
                student_name = row['student_name']
                embedding = pickle.loads(row['embedding'])
                results.append((student_id, student_name, embedding))
            
            return results
            
        except Exception as e:
            print(f"Error retrieving embeddings: {e}")
            return []
    
    def get_student_count(self) -> int:
        """Get total number of registered students"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM students")
            return cursor.fetchone()['count']
        except Exception as e:
            print(f"Error getting student count: {e}")
            return 0
    
    def log_attendance(self, student_id: Optional[str], status: str, 
                      similarity_score: Optional[float], processing_time_ms: float) -> bool:
        """
        Log an attendance attempt
        
        Args:
            student_id: Student ID (None for UNKNOWN)
            status: 'SUCCESS' or 'FAILURE'
            similarity_score: Cosine similarity score
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO attendance_logs (student_id, timestamp, status, similarity_score, processing_time_ms)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, datetime.now(), status, similarity_score, processing_time_ms))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error logging attendance: {e}")
            return False
    
    def get_logs(self, limit: int = 100, status_filter: Optional[str] = None) -> List[Dict]:
        """
        Retrieve attendance logs
        
        Args:
            limit: Maximum number of logs to retrieve
            status_filter: Filter by status ('SUCCESS' or 'FAILURE')
            
        Returns:
            List of log dictionaries
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM attendance_logs"
            params = []
            
            if status_filter:
                query += " WHERE status = ?"
                params.append(status_filter)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            logs = []
            for row in rows:
                logs.append({
                    'log_id': row['log_id'],
                    'student_id': row['student_id'] or 'UNKNOWN',
                    'timestamp': row['timestamp'],
                    'status': row['status'],
                    'similarity_score': row['similarity_score'],
                    'processing_time_ms': row['processing_time_ms']
                })
            
            return logs
            
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return []
    
    def get_log_statistics(self) -> Dict:
        """Get summary statistics for logs"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total attempts
            cursor.execute("SELECT COUNT(*) as total FROM attendance_logs")
            total = cursor.fetchone()['total']
            
            # Success count
            cursor.execute("SELECT COUNT(*) as success FROM attendance_logs WHERE status = 'SUCCESS'")
            success = cursor.fetchone()['success']
            
            # Average processing time
            cursor.execute("SELECT AVG(processing_time_ms) as avg_time FROM attendance_logs")
            avg_time = cursor.fetchone()['avg_time'] or 0
            
            success_rate = (success / total * 100) if total > 0 else 0
            
            return {
                'total_attempts': total,
                'successful_attempts': success,
                'failed_attempts': total - success,
                'success_rate': success_rate,
                'avg_processing_time_ms': avg_time
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def generate_dummy_embeddings(self, count: int = 5000):
        """
        Generate dummy embeddings for scale testing
        
        Args:
            count: Number of dummy embeddings to generate
        """
        print(f"Generating {count} dummy embeddings...")
        
        for i in range(count):
            student_id = f"DUMMY_{i:05d}"
            student_name = f"Dummy Student {i}"
            
            # Generate random normalized embedding
            embedding = np.random.randn(512).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)  # L2 normalize
            
            self.insert_student(student_id, student_name, embedding)
            
            if (i + 1) % 1000 == 0:
                print(f"Generated {i + 1}/{count} embeddings...")
        
        print(f"Successfully generated {count} dummy embeddings")
    
    def clear_dummy_data(self):
        """Remove all dummy data from database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE student_id LIKE 'DUMMY_%'")
            conn.commit()
            print("Dummy data cleared")
        except Exception as e:
            print(f"Error clearing dummy data: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


# Singleton instance
_db_instance = None

def get_database() -> Database:
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.init_db()
    return _db_instance
