from flask_login import UserMixin
from database import get_user_by_id, get_user_by_username, authenticate_user

class User(UserMixin):
    """User class for Flask-Login"""

    def __init__(self, user_data):
        self.id = str(user_data['id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.user_type = user_data['user_type']
        self.full_name = user_data['full_name']
        self.phone = user_data.get('phone')
        self.department_name = user_data.get('department_name')
        self.department_location = user_data.get('department_location')
        self.created_at = user_data['created_at']
        self._is_active = user_data['is_active']

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return bool(self._is_active)

    def is_fire_department(self):
        return self.user_type == 'fire_department'

    def is_regular_user(self):
        return self.user_type == 'user'

def load_user(user_id):
    """Load user by ID for Flask-Login"""
    user_data = get_user_by_id(int(user_id))
    if user_data:
        return User(user_data)
    return None

def login_user_by_credentials(username_or_email, password):
    """Authenticate and return User object"""
    user_data = authenticate_user(username_or_email, password)
    if user_data:
        return User(user_data)
    return None
