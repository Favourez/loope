#!/usr/bin/env python3
"""
Emergency Response App - Comprehensive API Endpoints
Provides RESTful API for all application functionality
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
import json
import datetime
from database import (
    get_emergency_reports, create_emergency_report, update_report_status,
    get_fire_departments, get_messages, create_message, delete_message,
    get_user_by_id, create_user, authenticate_user, get_user_by_username
)

# Create API Blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

def get_first_aid_practices():
    """Get first aid practices from current app"""
    try:
        from flask import current_app
        return current_app.config.get('FIRST_AID_PRACTICES', [])
    except:
        # Fallback data if app context is not available
        return [
            {
                'id': 1,
                'title': 'CPR (Cardiopulmonary Resuscitation)',
                'description': 'Life-saving technique for cardiac arrest',
                'icon': 'fas fa-heartbeat',
                'emergency_type': 'Cardiac Emergency',
                'image': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=300&fit=crop',
                'video_url': 'https://www.youtube.com/embed/TRVjwdNVgjs',
                'duration': '5-10 minutes',
                'difficulty': 'Intermediate',
                'keywords': ['cardiac arrest', 'heart attack', 'unconscious', 'no pulse', 'chest compressions']
            }
        ]

def api_key_required(f):
    """Decorator to require API key for certain endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or api_key != current_app.config.get('API_KEY', 'emergency-api-key-2024'):
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def json_response(data, status_code=200):
    """Helper function to create consistent JSON responses"""
    response = {
        'status': 'success' if status_code < 400 else 'error',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'data': data
    }
    return jsonify(response), status_code

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@api.route('/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user authentication"""
    try:
        data = request.get_json()
        if not data:
            return json_response({'error': 'No JSON data provided'}, 400)
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return json_response({'error': 'Username and password required'}, 400)
        
        user_data = authenticate_user(username, password)
        if user_data:
            # Remove sensitive data
            safe_user_data = {k: v for k, v in user_data.items() if k != 'password_hash'}
            return json_response({
                'message': 'Login successful',
                'user': safe_user_data,
                'token': f"token_{user_data['id']}_{datetime.datetime.utcnow().timestamp()}"
            })
        else:
            return json_response({'error': 'Invalid credentials'}, 401)
            
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@api.route('/auth/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    try:
        data = request.get_json()
        required_fields = ['username', 'email', 'password', 'full_name', 'phone']
        
        for field in required_fields:
            if not data.get(field):
                return json_response({'error': f'{field} is required'}, 400)
        
        user_id = create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            user_type=data.get('user_type', 'user'),
            full_name=data['full_name'],
            phone=data['phone'],
            department_name=data.get('department_name'),
            department_location=data.get('department_location')
        )
        
        return json_response({
            'message': 'User registered successfully',
            'user_id': user_id
        }, 201)
        
    except ValueError as e:
        return json_response({'error': str(e)}, 400)
    except Exception as e:
        return json_response({'error': str(e)}, 500)

# ============================================================================
# EMERGENCY REPORTS ENDPOINTS
# ============================================================================

@api.route('/emergencies', methods=['GET'])
@api_key_required
def api_get_emergencies():
    """Get all emergency reports with optional filtering"""
    try:
        # Query parameters
        status = request.args.get('status')
        severity = request.args.get('severity')
        limit = request.args.get('limit', type=int)
        
        reports = get_emergency_reports()
        
        # Apply filters
        if status:
            reports = [r for r in reports if r['status'] == status]
        if severity:
            reports = [r for r in reports if r['severity'] == severity]
        if limit:
            reports = reports[:limit]
        
        return json_response({
            'emergencies': reports,
            'total_count': len(reports)
        })
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@api.route('/emergencies', methods=['POST'])
@api_key_required
def api_create_emergency():
    """Create a new emergency report"""
    try:
        data = request.get_json()
        required_fields = ['emergency_type', 'location', 'description', 'severity']
        
        for field in required_fields:
            if not data.get(field):
                return json_response({'error': f'{field} is required'}, 400)
        
        # Get user_id from token or use anonymous
        user_id = data.get('user_id', 1)  # Default to test user
        
        report_id = create_emergency_report(
            user_id=user_id,
            location=data['location'],
            description=f"{data['emergency_type']}: {data['description']}",
            severity=data['severity'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            location_accuracy=data.get('accuracy')
        )
        
        return json_response({
            'message': 'Emergency report created successfully',
            'report_id': report_id
        }, 201)
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@api.route('/emergencies/<int:report_id>', methods=['GET'])
@api_key_required
def api_get_emergency(report_id):
    """Get specific emergency report"""
    try:
        reports = get_emergency_reports()
        report = next((r for r in reports if r['id'] == report_id), None)
        
        if not report:
            return json_response({'error': 'Emergency report not found'}, 404)
        
        return json_response({'emergency': report})
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@api.route('/emergencies/<int:report_id>/status', methods=['PUT'])
@api_key_required
def api_update_emergency_status(report_id):
    """Update emergency report status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return json_response({'error': 'Status is required'}, 400)
        
        valid_statuses = ['reported', 'responding', 'resolved', 'cancelled']
        if new_status not in valid_statuses:
            return json_response({'error': f'Invalid status. Must be one of: {valid_statuses}'}, 400)
        
        update_report_status(report_id, new_status)
        
        return json_response({
            'message': 'Emergency status updated successfully',
            'report_id': report_id,
            'new_status': new_status
        })
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

# ============================================================================
# FIRE DEPARTMENTS ENDPOINTS
# ============================================================================

@api.route('/fire-departments', methods=['GET'])
@api_key_required
def api_get_fire_departments():
    """Get all fire departments"""
    try:
        departments = get_fire_departments()
        return json_response({
            'fire_departments': departments,
            'total_count': len(departments)
        })
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

# ============================================================================
# MESSAGES ENDPOINTS
# ============================================================================

@api.route('/messages', methods=['GET'])
@api_key_required
def api_get_messages():
    """Get community messages"""
    try:
        limit = request.args.get('limit', 50, type=int)
        messages = get_messages(limit=limit)
        
        return json_response({
            'messages': messages,
            'total_count': len(messages)
        })
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@api.route('/messages', methods=['POST'])
@api_key_required
def api_create_message():
    """Create a new community message"""
    try:
        data = request.get_json()
        required_fields = ['content', 'message_type']
        
        for field in required_fields:
            if not data.get(field):
                return json_response({'error': f'{field} is required'}, 400)
        
        user_id = data.get('user_id', 1)  # Default to test user
        
        message_id = create_message(
            user_id=user_id,
            content=data['content'],
            message_type=data['message_type']
        )
        
        return json_response({
            'message': 'Message created successfully',
            'message_id': message_id
        }, 201)
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@api.route('/messages/<int:message_id>', methods=['DELETE'])
@api_key_required
def api_delete_message(message_id):
    """Delete a community message"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        delete_message(message_id, user_id)
        
        return json_response({
            'message': 'Message deleted successfully',
            'message_id': message_id
        })
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

# ============================================================================
# FIRST AID ENDPOINTS
# ============================================================================

@api.route('/first-aid', methods=['GET'])
def api_get_first_aid_practices():
    """Get all first aid practices"""
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        
        practices = get_first_aid_practices()
        
        # Apply filters
        if category:
            practices = [p for p in practices if p['emergency_type'] == category]
        if difficulty:
            practices = [p for p in practices if p.get('difficulty') == difficulty]
        
        return json_response({
            'first_aid_practices': practices,
            'total_count': len(practices)
        })
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

@api.route('/first-aid/<int:practice_id>', methods=['GET'])
def api_get_first_aid_practice(practice_id):
    """Get specific first aid practice"""
    try:
        practices = get_first_aid_practices()
        practice = next((p for p in practices if p['id'] == practice_id), None)
        
        if not practice:
            return json_response({'error': 'First aid practice not found'}, 404)
        
        return json_response({'first_aid_practice': practice})
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@api.route('/health', methods=['GET'])
def api_health_check():
    """Health check endpoint"""
    return json_response({
        'status': 'healthy',
        'version': '1.0.0',
        'service': 'Emergency Response API'
    })

@api.route('/status', methods=['GET'])
@api_key_required
def api_system_status():
    """System status endpoint with detailed information"""
    try:
        # Get system statistics
        reports = get_emergency_reports()
        messages = get_messages(limit=1000)
        departments = get_fire_departments()
        
        return json_response({
            'system_status': 'operational',
            'statistics': {
                'total_emergency_reports': len(reports),
                'pending_emergencies': len([r for r in reports if r['status'] == 'pending']),
                'total_messages': len(messages),
                'total_fire_departments': len(departments),
                'total_first_aid_practices': len(get_first_aid_practices())
            },
            'uptime': 'Available',
            'last_updated': datetime.datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return json_response({'error': str(e)}, 500)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@api.errorhandler(404)
def api_not_found(error):
    return json_response({'error': 'Endpoint not found'}, 404)

@api.errorhandler(405)
def api_method_not_allowed(error):
    return json_response({'error': 'Method not allowed'}, 405)

@api.errorhandler(500)
def api_internal_error(error):
    return json_response({'error': 'Internal server error'}, 500)
