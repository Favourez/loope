from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import json
import os
import time
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_flask_exporter import PrometheusMetrics
from database import (init_database, create_user, create_emergency_report, get_emergency_reports,
                     update_report_status, get_fire_departments, create_message, get_messages,
                     delete_message, like_message, update_user_profile, change_user_password,
                     delete_user_account, verify_password, get_user_by_id, get_user_by_email)
from auth import User, load_user, login_user_by_credentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration (you can move these to environment variables)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'your-email@gmail.com'  # Replace with your email
EMAIL_PASSWORD = 'your-app-password'  # Replace with your app password
EMAIL_FROM = 'Emergency Response App <your-email@gmail.com>'

def send_email_notification(to_email, subject, message, html_message=None):
    """Send email notification"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email

        # Add text part
        text_part = MIMEText(message, 'plain')
        msg.attach(text_part)

        # Add HTML part if provided
        if html_message:
            html_part = MIMEText(html_message, 'html')
            msg.attach(html_part)

        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user_callback(user_id):
    return load_user(user_id)

# Initialize database
init_database()

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Custom metrics for emergency app
emergency_reports_total = Counter('emergency_reports_total', 'Total number of emergency reports', ['severity', 'type'])
first_aid_views_total = Counter('first_aid_views_total', 'Total first aid guide views', ['practice_id', 'practice_name'])
page_views_total = Counter('page_views_total', 'Total page views', ['page'])
response_time_histogram = Histogram('response_time_seconds', 'Response time in seconds', ['endpoint'])
active_users_gauge = Gauge('active_users', 'Number of active users')
system_health_gauge = Gauge('system_health_score', 'System health score (0-100)')

# Track active users (simplified)
active_users = set()

# Add metrics info endpoint
metrics.info('emergency_app_info', 'Emergency Response App Information', version='1.0.0')

# Sample data for first aid practices
FIRST_AID_PRACTICES = [
    {
        'id': 1,
        'title': 'CPR (Cardiopulmonary Resuscitation)',
        'description': 'Life-saving technique for cardiac arrest',
        'icon': 'fas fa-heartbeat',
        'emergency_type': 'Cardiac Emergency'
    },
    {
        'id': 2,
        'title': 'Choking Relief (Heimlich Maneuver)',
        'description': 'Emergency procedure for airway obstruction',
        'icon': 'fas fa-lungs',
        'emergency_type': 'Airway Emergency'
    },
    {
        'id': 3,
        'title': 'Burn Treatment',
        'description': 'Immediate care for thermal injuries',
        'icon': 'fas fa-fire',
        'emergency_type': 'Thermal Emergency'
    },
    {
        'id': 4,
        'title': 'Wound Care and Bleeding Control',
        'description': 'Managing cuts and severe bleeding',
        'icon': 'fas fa-band-aid',
        'emergency_type': 'Trauma Emergency'
    },
    {
        'id': 5,
        'title': 'Fracture Management',
        'description': 'Stabilizing broken bones',
        'icon': 'fas fa-bone',
        'emergency_type': 'Orthopedic Emergency'
    },
    {
        'id': 6,
        'title': 'Shock Treatment',
        'description': 'Managing life-threatening shock',
        'icon': 'fas fa-exclamation-triangle',
        'emergency_type': 'Critical Emergency'
    },
    {
        'id': 7,
        'title': 'Allergic Reaction Response',
        'description': 'Managing severe allergic reactions',
        'icon': 'fas fa-allergies',
        'emergency_type': 'Allergic Emergency'
    },
    {
        'id': 8,
        'title': 'Heat Stroke Treatment',
        'description': 'Managing heat-related emergencies',
        'icon': 'fas fa-thermometer-full',
        'emergency_type': 'Environmental Emergency'
    },
    {
        'id': 9,
        'title': 'Hypothermia Management',
        'description': 'Treating dangerous cold exposure',
        'icon': 'fas fa-snowflake',
        'emergency_type': 'Environmental Emergency'
    },
    {
        'id': 10,
        'title': 'Poisoning Response',
        'description': 'Emergency response to toxic exposure',
        'icon': 'fas fa-skull-crossbones',
        'emergency_type': 'Toxicological Emergency'
    }
]

@app.route('/')
def welcome():
    page_views_total.labels(page='welcome').inc()
    if current_user.is_authenticated:
        if current_user.is_fire_department():
            return redirect(url_for('fire_department_dashboard'))
        else:
            return redirect(url_for('landing'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            user_type = request.form['user_type']
            full_name = request.form['full_name']
            phone = request.form.get('phone')
            department_name = request.form.get('department_name')
            department_location = request.form.get('department_location')

            # Validation
            if password != confirm_password:
                return render_template('register.html', error='Passwords do not match')

            if len(password) < 6:
                return render_template('register.html', error='Password must be at least 6 characters long')

            if user_type not in ['user', 'fire_department']:
                return render_template('register.html', error='Invalid user type')

            # Create user
            user_id = create_user(
                username=username,
                email=email,
                password=password,
                user_type=user_type,
                full_name=full_name,
                phone=phone,
                department_name=department_name,
                department_location=department_location
            )

            return redirect(url_for('login', success='Registration successful! Please log in.'))

        except ValueError as e:
            return render_template('register.html', error=str(e))
        except Exception as e:
            return render_template('register.html', error='Registration failed. Please try again.')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))

    success_message = request.args.get('success')

    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        remember_me = 'remember_me' in request.form

        user = login_user_by_credentials(username_or_email, password)
        if user:
            login_user(user, remember=remember_me)
            user_id = request.remote_addr
            active_users.add(user_id)
            active_users_gauge.set(len(active_users))

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if user.is_fire_department():
                return redirect(url_for('fire_department_dashboard'))
            else:
                return redirect(url_for('landing'))
        else:
            return render_template('login.html', error='Invalid username/email or password')

    return render_template('login.html', success=success_message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            try:
                full_name = request.form['full_name']
                email = request.form['email']
                username = request.form['username']
                phone = request.form.get('phone')
                department_name = request.form.get('department_name')
                department_location = request.form.get('department_location')

                success = update_user_profile(
                    user_id=current_user.id,
                    full_name=full_name,
                    email=email,
                    username=username,
                    phone=phone,
                    department_name=department_name,
                    department_location=department_location
                )

                if success:
                    return render_template('profile.html', success='Profile updated successfully!')
                else:
                    return render_template('profile.html', error='Failed to update profile. Username or email may already exist.')

            except Exception as e:
                return render_template('profile.html', error='Failed to update profile.')

        elif action == 'change_password':
            try:
                current_password = request.form['current_password']
                new_password = request.form['new_password']

                # Verify current password
                user_data = get_user_by_id(current_user.id)
                if not verify_password(current_password, user_data['password_hash']):
                    return render_template('profile.html', error='Current password is incorrect.')

                # Change password
                change_user_password(current_user.id, new_password)
                return render_template('profile.html', success='Password changed successfully!')

            except Exception as e:
                return render_template('profile.html', error='Failed to change password.')

        elif action == 'delete_account':
            try:
                delete_user_account(current_user.id)
                logout_user()
                return redirect(url_for('login', success='Account deleted successfully.'))
            except Exception as e:
                return render_template('profile.html', error='Failed to delete account.')

    return render_template('profile.html')

@app.route('/landing')
@login_required
def landing():
    if current_user.is_fire_department():
        return redirect(url_for('fire_department_dashboard'))

    page_views_total.labels(page='landing').inc()
    user_id = request.remote_addr
    active_users.add(user_id)
    active_users_gauge.set(len(active_users))
    return render_template('landing.html')

@app.route('/fire-department-dashboard')
@login_required
def fire_department_dashboard():
    if not current_user.is_fire_department():
        return redirect(url_for('landing'))

    page_views_total.labels(page='fire_department_dashboard').inc()

    # Get emergency reports
    emergency_reports = get_emergency_reports(limit=20)
    active_reports = [r for r in emergency_reports if r['status'] == 'reported']
    responding_reports = [r for r in emergency_reports if r['status'] == 'responding']

    # Count resolved reports today
    from datetime import date
    today = date.today().isoformat()
    resolved_today = len([r for r in emergency_reports if r['status'] == 'resolved' and r['updated_at'].startswith(today)])

    return render_template('fire_department_landing.html',
                         emergency_reports=emergency_reports,
                         active_reports=active_reports,
                         responding_reports=responding_reports,
                         resolved_today=resolved_today)

@app.route('/map')
@login_required
def map_page():
    page_views_total.labels(page='map').inc()
    return render_template('map.html')

@app.route('/test-map')
def test_map():
    with open('test_map.html', 'r') as f:
        return f.read()

@app.route('/test-location')
def test_location():
    return render_template('location_test.html')

@app.route('/messages')
@login_required
def messages():
    page_views_total.labels(page='messages').inc()
    messages_list = get_messages(limit=50)
    return render_template('messages.html', messages=messages_list, online_users=1)

@app.route('/send-message', methods=['POST'])
@login_required
def send_message():
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'general')

        if not content:
            return jsonify({'success': False, 'message': 'Message content is required'})

        if len(content) > 500:
            return jsonify({'success': False, 'message': 'Message too long (max 500 characters)'})

        message_id = create_message(current_user.id, content, message_type)
        return jsonify({'success': True, 'message_id': message_id})

    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to send message'}), 500

@app.route('/get-messages')
@login_required
def get_messages_api():
    try:
        messages_list = get_messages(limit=50)
        return jsonify({'success': True, 'messages': messages_list})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to load messages'}), 500

@app.route('/delete-message', methods=['POST'])
@login_required
def delete_message_api():
    try:
        data = request.get_json()
        message_id = data.get('message_id')

        success = delete_message(message_id, current_user.id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Unauthorized or message not found'})

    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to delete message'}), 500

@app.route('/like-message', methods=['POST'])
@login_required
def like_message_api():
    try:
        data = request.get_json()
        message_id = data.get('message_id')

        likes = like_message(message_id)
        return jsonify({'success': True, 'likes': likes})

    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to like message'}), 500

@app.route('/help')
@login_required
def help_page():
    page_views_total.labels(page='help').inc()
    return render_template('help.html')

@app.route('/settings')
@login_required
def settings():
    page_views_total.labels(page='settings').inc()
    return render_template('settings.html')

@app.route('/first-aid')
@login_required
def first_aid():
    page_views_total.labels(page='first_aid').inc()
    first_aid_views_total.labels(practice_id='overview', practice_name='overview').inc()
    return render_template('first_aid.html', practices=FIRST_AID_PRACTICES)

@app.route('/first-aid/<int:practice_id>')
@login_required
def first_aid_detail(practice_id):
    practice = next((p for p in FIRST_AID_PRACTICES if p['id'] == practice_id), None)
    if not practice:
        return redirect(url_for('first_aid'))

    page_views_total.labels(page='first_aid_detail').inc()
    first_aid_views_total.labels(practice_id=str(practice_id), practice_name=practice['title']).inc()
    return render_template('first_aid_detail.html', practice=practice)

@app.route('/privacy')
def privacy():
    page_views_total.labels(page='privacy').inc()
    return render_template('privacy.html')

@app.route('/guidelines')
def guidelines():
    page_views_total.labels(page='guidelines').inc()
    return render_template('guidelines.html')

@app.route('/report-emergency', methods=['POST'])
@login_required
def report_emergency():
    data = request.get_json()

    # Extract emergency data for metrics
    severity = data.get('severity', 'unknown') if data else 'unknown'
    emergency_type = 'fire'  # Default to fire since this is a fire emergency app

    # Increment emergency reports counter
    emergency_reports_total.labels(severity=severity, type=emergency_type).inc()

    # Update system health (simulate decreasing health with more emergencies)
    try:
        total_reports = sum(emergency_reports_total._value.values())
        current_health = max(50, 100 - (total_reports * 2))
        system_health_gauge.set(current_health)
    except:
        system_health_gauge.set(95)  # Default health if calculation fails

    # Save to database
    try:
        report_id = create_emergency_report(
            user_id=current_user.id,
            location=data.get('location', ''),
            description=data.get('description', ''),
            severity=severity,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            location_accuracy=data.get('location_accuracy')
        )

        # Send email confirmation to user
        try:
            send_emergency_confirmation_email(current_user, report_id, data)
        except Exception as email_error:
            print(f"Failed to send confirmation email: {email_error}")

        return jsonify({'status': 'success', 'message': 'Emergency reported successfully', 'report_id': report_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to save emergency report'}), 500

def send_emergency_confirmation_email(user, report_id, emergency_data):
    """Send email confirmation for emergency report"""
    subject = f"Emergency Report Confirmation - Report #{report_id}"

    # Create text message
    text_message = f"""
Dear {user.full_name},

Your emergency report has been successfully submitted and received by our emergency response system.

EMERGENCY REPORT DETAILS:
Report ID: #{report_id}
Location: {emergency_data.get('location', 'Not specified')}
Severity: {emergency_data.get('severity', 'Unknown').upper()}
Description: {emergency_data.get('description', 'No description provided')}
Reported at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

GPS Coordinates: {'Available' if emergency_data.get('latitude') else 'Not available'}
{f"Latitude: {emergency_data.get('latitude')}" if emergency_data.get('latitude') else ''}
{f"Longitude: {emergency_data.get('longitude')}" if emergency_data.get('longitude') else ''}

WHAT HAPPENS NEXT:
1. Emergency services have been automatically notified
2. Fire departments in your area will receive this report immediately
3. Response teams will be dispatched based on severity and location
4. You may be contacted for additional information if needed

IMPORTANT REMINDERS:
- If this is a life-threatening emergency, call 118 immediately
- Keep your phone accessible in case emergency responders need to contact you
- Follow any evacuation orders or safety instructions from authorities

Thank you for using our emergency response system. Your safety is our priority.

Emergency Response Team
Fire Emergency Response App

For urgent matters, call:
Fire: 118 | Police: 117 | Medical: 119
"""

    # Create HTML message
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .report-details {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0; }}
        .severity-{emergency_data.get('severity', 'low')} {{
            color: {'#dc3545' if emergency_data.get('severity') == 'critical' else
                   '#fd7e14' if emergency_data.get('severity') == 'high' else
                   '#ffc107' if emergency_data.get('severity') == 'medium' else '#28a745'};
            font-weight: bold;
        }}
        .next-steps {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .emergency-contacts {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Emergency Report Confirmation</h1>
        <p>Report #{report_id} Successfully Submitted</p>
    </div>

    <div class="content">
        <p>Dear <strong>{user.full_name}</strong>,</p>

        <p>Your emergency report has been successfully submitted and received by our emergency response system.</p>

        <div class="report-details">
            <h3>📋 Emergency Report Details</h3>
            <p><strong>Report ID:</strong> #{report_id}</p>
            <p><strong>Location:</strong> {emergency_data.get('location', 'Not specified')}</p>
            <p><strong>Severity:</strong> <span class="severity-{emergency_data.get('severity', 'low')}">{emergency_data.get('severity', 'Unknown').upper()}</span></p>
            <p><strong>Description:</strong> {emergency_data.get('description', 'No description provided')}</p>
            <p><strong>Reported at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>GPS Coordinates:</strong> {'✅ Available' if emergency_data.get('latitude') else '❌ Not available'}</p>
            {f"<p><strong>Latitude:</strong> {emergency_data.get('latitude')}</p>" if emergency_data.get('latitude') else ''}
            {f"<p><strong>Longitude:</strong> {emergency_data.get('longitude')}</p>" if emergency_data.get('longitude') else ''}
        </div>

        <div class="next-steps">
            <h3>🚀 What Happens Next</h3>
            <ol>
                <li>Emergency services have been automatically notified</li>
                <li>Fire departments in your area will receive this report immediately</li>
                <li>Response teams will be dispatched based on severity and location</li>
                <li>You may be contacted for additional information if needed</li>
            </ol>
        </div>

        <div class="emergency-contacts">
            <h3>⚠️ Important Reminders</h3>
            <ul>
                <li>If this is a life-threatening emergency, call <strong>118</strong> immediately</li>
                <li>Keep your phone accessible in case emergency responders need to contact you</li>
                <li>Follow any evacuation orders or safety instructions from authorities</li>
            </ul>
        </div>

        <p>Thank you for using our emergency response system. Your safety is our priority.</p>
    </div>

    <div class="footer">
        <p><strong>Emergency Response Team</strong><br>
        Fire Emergency Response App</p>
        <p>For urgent matters, call:<br>
        🔥 Fire: 118 | 👮 Police: 117 | 🚑 Medical: 119</p>
    </div>
</body>
</html>
"""

    # Send the email
    return send_email_notification(user.email, subject, text_message, html_message)

@app.route('/update-report-status', methods=['POST'])
@login_required
def update_report_status_route():
    if not current_user.is_fire_department():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    report_id = data.get('report_id')
    status = data.get('status')
    department_id = data.get('department_id')

    try:
        update_report_status(report_id, status, department_id)
        return jsonify({'success': True, 'message': 'Report status updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to update report status'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'active_users': len(active_users),
        'total_emergency_reports': sum(emergency_reports_total._value.values()) if hasattr(emergency_reports_total, '_value') else 0,
        'system_health_score': system_health_gauge._value._value if hasattr(system_health_gauge, '_value') else 100
    }
    return jsonify(health_status)

@app.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/map-data')
def get_map_data():
    """API endpoint to get map data for emergencies, hospitals, and fire stations"""
    map_data = {
        'emergencies': [
            {
                'id': 1,
                'type': 'fire',
                'title': 'House Fire',
                'location': 'Bastos, Yaoundé',
                'coordinates': [3.8691, 11.5174],
                'severity': 'high',
                'time': '15 minutes ago',
                'description': 'Residential fire in Bastos neighborhood',
                'status': 'active'
            },
            {
                'id': 2,
                'type': 'fire',
                'title': 'Vehicle Fire',
                'location': 'Douala Port',
                'coordinates': [4.0511, 9.7679],
                'severity': 'medium',
                'time': '32 minutes ago',
                'description': 'Vehicle fire near port area',
                'status': 'responding'
            },
            {
                'id': 3,
                'type': 'fire',
                'title': 'Brush Fire',
                'location': 'Bamenda Hills',
                'coordinates': [5.9631, 10.1591],
                'severity': 'low',
                'time': '1 hour ago',
                'description': 'Small brush fire on hillside',
                'status': 'contained'
            }
        ],
        'hospitals': [
            {
                'name': 'Yaoundé Central Hospital',
                'coordinates': [3.8634, 11.5167],
                'type': 'General Hospital',
                'emergency': True,
                'phone': '119'
            },
            {
                'name': 'Douala General Hospital',
                'coordinates': [4.0435, 9.7043],
                'type': 'General Hospital',
                'emergency': True,
                'phone': '119'
            },
            {
                'name': 'Bamenda Regional Hospital',
                'coordinates': [5.9597, 10.1463],
                'type': 'Regional Hospital',
                'emergency': True,
                'phone': '119'
            },
            {
                'name': 'Garoua Regional Hospital',
                'coordinates': [9.3265, 13.3981],
                'type': 'Regional Hospital',
                'emergency': True,
                'phone': '119'
            }
        ],
        'fire_stations': [
            {
                'name': 'Yaoundé Fire Station',
                'coordinates': [3.8480, 11.5021],
                'type': 'Main Station',
                'phone': '118',
                'vehicles': 5
            },
            {
                'name': 'Douala Fire Station',
                'coordinates': [4.0511, 9.7679],
                'type': 'Port Station',
                'phone': '118',
                'vehicles': 8
            },
            {
                'name': 'Bamenda Fire Station',
                'coordinates': [5.9631, 10.1591],
                'type': 'Regional Station',
                'phone': '118',
                'vehicles': 3
            }
        ]
    }
    return jsonify(map_data)

# Background task to simulate system health updates
@app.before_request
def before_request():
    # Update system health score based on various factors
    try:
        base_health = 95
        total_reports = sum(emergency_reports_total._value.values()) if hasattr(emergency_reports_total, '_value') else 0
        emergency_impact = min(30, total_reports * 2)
        user_load_impact = min(10, len(active_users) * 0.5)

        current_health = max(0, base_health - emergency_impact - user_load_impact)
        system_health_gauge.set(current_health)
    except Exception as e:
        # Fallback to default health if calculation fails
        system_health_gauge.set(95)

if __name__ == '__main__':
    # Set initial system health
    system_health_gauge.set(100)
    app.run(debug=True, host='0.0.0.0', port=3000)

