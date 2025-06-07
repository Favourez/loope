from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import json
import os
import time
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_flask_exporter import PrometheusMetrics
from database import init_database, create_user, create_emergency_report, get_emergency_reports, update_report_status, get_fire_departments
from auth import User, load_user, login_user_by_credentials

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
        username = request.form['username']
        password = request.form['password']
        remember_me = 'remember_me' in request.form

        user = login_user_by_credentials(username, password)
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
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html', success=success_message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

@app.route('/messages')
@login_required
def messages():
    page_views_total.labels(page='messages').inc()
    return render_template('messages.html')

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
        return jsonify({'status': 'success', 'message': 'Emergency reported successfully', 'report_id': report_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to save emergency report'}), 500

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

