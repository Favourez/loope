from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import time
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

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
    user_id = request.remote_addr
    active_users.add(user_id)
    active_users_gauge.set(len(active_users))
    return render_template('welcome.html')

@app.route('/landing')
def landing():
    page_views_total.labels(page='landing').inc()
    user_id = request.remote_addr
    active_users.add(user_id)
    active_users_gauge.set(len(active_users))
    return render_template('landing.html')

@app.route('/map')
def map_page():
    page_views_total.labels(page='map').inc()
    return render_template('map.html')

@app.route('/messages')
def messages():
    page_views_total.labels(page='messages').inc()
    return render_template('messages.html')

@app.route('/help')
def help_page():
    page_views_total.labels(page='help').inc()
    return render_template('help.html')

@app.route('/settings')
def settings():
    page_views_total.labels(page='settings').inc()
    return render_template('settings.html')

@app.route('/first-aid')
def first_aid():
    page_views_total.labels(page='first_aid').inc()
    first_aid_views_total.labels(practice_id='overview', practice_name='overview').inc()
    return render_template('first_aid.html', practices=FIRST_AID_PRACTICES)

@app.route('/first-aid/<int:practice_id>')
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

    # Here you would typically save to database
    # For now, we'll just return a success response
    return jsonify({'status': 'success', 'message': 'Emergency reported successfully'})

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
