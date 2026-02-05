"""
Database Migration Script
Adds user management methods to Database class and creates default admin
"""
import sys
sys.path.insert(0, 'C:\\Users\\mohan\\.gemini\\antigravity\\playground\\triple-void')

from db.database import Database, get_database
from utils.auth_utils import hash_password

# Add methods to Database class
from db.database_extensions import (
    create_user, get_user_by_username, get_all_users, toggle_user_status,
    get_today_attendance_count, check_attendance_today,
    get_student_attendance_all, get_student_attendance_month,
    get_student_attendance_week, get_student_monthly_attendance_count
)

# Attach methods to Database class
Database.create_user = create_user
Database.get_user_by_username = get_user_by_username
Database.get_all_users = get_all_users
Database.toggle_user_status = toggle_user_status
Database.get_today_attendance_count = get_today_attendance_count
Database.check_attendance_today = check_attendance_today
Database.get_student_attendance_all = get_student_attendance_all
Database.get_student_attendance_month = get_student_attendance_month
Database.get_student_attendance_week = get_student_attendance_week
Database.get_student_monthly_attendance_count = get_student_monthly_attendance_count

print("✅ Database methods extended successfully")

# Create default admin user
db = get_database()

# Check if admin already exists
existing_admin = db.get_user_by_username('admin')

if not existing_admin:
    admin_password = hash_password('admin123')
    user_id = db.create_user('ADMIN001', 'Administrator', 'admin', admin_password, 'admin')
    if user_id:
        print(f"✅ Default admin created (ID: {user_id})")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print("❌ Failed to create admin user")
else:
    print("ℹ️  Admin user already exists")

print("\n✅ Migration complete!")
