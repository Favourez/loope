import sqlite3
import bcrypt
from datetime import datetime
import os

DATABASE_PATH = 'emergency_app.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()

    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK (user_type IN ('user', 'fire_department')),
            full_name TEXT NOT NULL,
            phone TEXT,
            department_name TEXT,
            department_location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    # Create emergency_reports table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS emergency_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            location TEXT NOT NULL,
            description TEXT,
            severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
            status TEXT DEFAULT 'reported' CHECK (status IN ('reported', 'responding', 'resolved', 'cancelled')),
            latitude REAL,
            longitude REAL,
            location_accuracy REAL,
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_department_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (assigned_department_id) REFERENCES users (id)
        )
    ''')

    # Add location_accuracy column if it doesn't exist (for existing databases)
    try:
        conn.execute('ALTER TABLE emergency_reports ADD COLUMN location_accuracy REAL')
        conn.commit()
        print("Added location_accuracy column to existing database")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # Create sessions table for user sessions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create messages table for community chat
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            message_type TEXT DEFAULT 'general' CHECK (message_type IN ('general', 'info', 'alert', 'emergency')),
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_user(username, email, password, user_type, full_name, phone=None, department_name=None, department_location=None):
    """Create a new user"""
    conn = get_db_connection()

    try:
        password_hash = hash_password(password)

        cursor = conn.execute('''
            INSERT INTO users (username, email, password_hash, user_type, full_name, phone, department_name, department_location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, user_type, full_name, phone, department_name, department_location))

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError as e:
        conn.close()
        if 'username' in str(e):
            raise ValueError("Username already exists")
        elif 'email' in str(e):
            raise ValueError("Email already exists")
        else:
            raise ValueError("User creation failed")

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND is_active = 1',
        (username,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ? AND is_active = 1',
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    user = get_user_by_username(username)
    if user and verify_password(password, user['password_hash']):
        return user
    return None

def create_emergency_report(user_id, location, description, severity, latitude=None, longitude=None, location_accuracy=None):
    """Create a new emergency report"""
    conn = get_db_connection()

    cursor = conn.execute('''
        INSERT INTO emergency_reports (user_id, location, description, severity, latitude, longitude, location_accuracy)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, location, description, severity, latitude, longitude, location_accuracy))

    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_emergency_reports(limit=50, status=None, department_id=None):
    """Get emergency reports with optional filtering"""
    conn = get_db_connection()
    
    query = '''
        SELECT er.*, u.full_name as reporter_name, u.phone as reporter_phone
        FROM emergency_reports er
        LEFT JOIN users u ON er.user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    if status:
        query += ' AND er.status = ?'
        params.append(status)
    
    if department_id:
        query += ' AND er.assigned_department_id = ?'
        params.append(department_id)
    
    query += ' ORDER BY er.reported_at DESC LIMIT ?'
    params.append(limit)
    
    reports = conn.execute(query, params).fetchall()
    conn.close()
    
    return [dict(report) for report in reports]

def update_report_status(report_id, status, department_id=None):
    """Update emergency report status"""
    conn = get_db_connection()
    
    if department_id:
        conn.execute('''
            UPDATE emergency_reports 
            SET status = ?, assigned_department_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, department_id, report_id))
    else:
        conn.execute('''
            UPDATE emergency_reports 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, report_id))
    
    conn.commit()
    conn.close()

def get_fire_departments():
    """Get all fire departments"""
    conn = get_db_connection()
    departments = conn.execute(
        'SELECT * FROM users WHERE user_type = "fire_department" AND is_active = 1'
    ).fetchall()
    conn.close()
    return [dict(dept) for dept in departments]

def create_message(user_id, content, message_type='general'):
    """Create a new message"""
    conn = get_db_connection()

    cursor = conn.execute('''
        INSERT INTO messages (user_id, content, message_type)
        VALUES (?, ?, ?)
    ''', (user_id, content, message_type))

    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id

def get_messages(limit=50):
    """Get recent messages with user information"""
    conn = get_db_connection()

    messages = conn.execute('''
        SELECT m.*, u.full_name, u.user_type, u.username
        FROM messages m
        LEFT JOIN users u ON m.user_id = u.id
        WHERE m.is_deleted = 0
        ORDER BY m.created_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()

    conn.close()
    return [dict(message) for message in reversed(messages)]

def delete_message(message_id, user_id):
    """Delete a message (soft delete)"""
    conn = get_db_connection()

    # Check if user owns the message
    message = conn.execute(
        'SELECT user_id FROM messages WHERE id = ? AND is_deleted = 0',
        (message_id,)
    ).fetchone()

    if not message or message['user_id'] != user_id:
        conn.close()
        return False

    # Soft delete the message
    conn.execute('''
        UPDATE messages
        SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (message_id,))

    conn.commit()
    conn.close()
    return True

def like_message(message_id):
    """Increment likes for a message"""
    conn = get_db_connection()

    conn.execute('''
        UPDATE messages
        SET likes = likes + 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND is_deleted = 0
    ''', (message_id,))

    # Get updated likes count
    result = conn.execute(
        'SELECT likes FROM messages WHERE id = ?',
        (message_id,)
    ).fetchone()

    conn.commit()
    conn.close()

    return result['likes'] if result else 0

def update_user_profile(user_id, full_name, email, username, phone=None, department_name=None, department_location=None):
    """Update user profile information"""
    conn = get_db_connection()

    try:
        conn.execute('''
            UPDATE users
            SET full_name = ?, email = ?, username = ?, phone = ?,
                department_name = ?, department_location = ?
            WHERE id = ?
        ''', (full_name, email, username, phone, department_name, department_location, user_id))

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def change_user_password(user_id, new_password):
    """Change user password"""
    conn = get_db_connection()

    password_hash = hash_password(new_password)

    conn.execute('''
        UPDATE users
        SET password_hash = ?
        WHERE id = ?
    ''', (password_hash, user_id))

    conn.commit()
    conn.close()
    return True

def delete_user_account(user_id):
    """Delete user account (soft delete)"""
    conn = get_db_connection()

    conn.execute('''
        UPDATE users
        SET is_active = 0
        WHERE id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()
    return True

# Initialize database when module is imported
if __name__ == "__main__":
    init_database()
