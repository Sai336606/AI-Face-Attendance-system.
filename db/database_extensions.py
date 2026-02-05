"""
Database Extensions for User Management
Additional methods to add to Database class
"""

# Add these methods to the Database class in database.py

def create_user(self, student_id: str, name: str, username: str, password_hash: str, role: str = 'student'):
    """Create new user account"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (student_id, name, username, password, role)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, name, username, password_hash, role))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user_by_username(self, username: str):
    """Get user by username"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_all_users(self):
    """Get all users"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def toggle_user_status(self, user_id: int, is_active: bool):
    """Enable/disable user account"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error toggling user status: {e}")
        return False

def get_today_attendance_count(self):
    """Get count of successful attendance today"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT student_id) 
            FROM attendance_logs 
            WHERE DATE(timestamp) = DATE('now') AND status = 'SUCCESS'
        """)
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error getting today's attendance: {e}")
        return 0

def check_attendance_today(self, student_id: str):
    """Check if student already marked attendance today"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM attendance_logs 
            WHERE student_id = ? AND DATE(timestamp) = DATE('now') AND status = 'SUCCESS'
        """, (student_id,))
        return cursor.fetchone()[0] > 0
    except Exception as e:
        print(f"Error checking attendance: {e}")
        return False

def get_student_attendance_all(self, student_id: str):
    """Get all attendance records for student"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(timestamp), TIME(timestamp), status, similarity_score, processing_time_ms
            FROM attendance_logs 
            WHERE student_id = ? AND status = 'SUCCESS'
            ORDER BY timestamp DESC
        """, (student_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting attendance: {e}")
        return []

def get_student_attendance_month(self, student_id: str):
    """Get this month's attendance records"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(timestamp), TIME(timestamp), status, similarity_score, processing_time_ms
            FROM attendance_logs 
            WHERE student_id = ? 
            AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
            AND status = 'SUCCESS'
            ORDER BY timestamp DESC
        """, (student_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting monthly attendance: {e}")
        return []

def get_student_attendance_week(self, student_id: str):
    """Get this week's attendance records"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DATE(timestamp), TIME(timestamp), status, similarity_score, processing_time_ms
            FROM attendance_logs 
            WHERE student_id = ? 
            AND DATE(timestamp) >= DATE('now', '-7 days')
            AND status = 'SUCCESS'
            ORDER BY timestamp DESC
        """, (student_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting weekly attendance: {e}")
        return []

def get_student_monthly_attendance_count(self, student_id: str):
    """Get count of days present this month"""
    try:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT DATE(timestamp))
            FROM attendance_logs 
            WHERE student_id = ? 
            AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
            AND status = 'SUCCESS'
        """, (student_id,))
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error getting monthly count: {e}")
        return 0
