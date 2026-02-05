"""
Database models for Face Attendance POC
Defines SQLite table schemas
"""

CREATE_STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    student_name TEXT NOT NULL,
    embedding BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_ATTENDANCE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS attendance_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL CHECK(status IN ('SUCCESS', 'FAILURE')),
    similarity_score REAL,
    processing_time_ms REAL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
"""

# Index for faster queries
CREATE_LOGS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
ON attendance_logs(timestamp DESC)
"""

CREATE_LOGS_STATUS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_logs_status 
ON attendance_logs(status)
"""
