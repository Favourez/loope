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
        'emergency_type': 'Cardiac Emergency',
        'image': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/TRVjwdNVgjs',
        'duration': '5-10 minutes',
        'difficulty': 'Intermediate',
        'keywords': ['cardiac arrest', 'heart attack', 'unconscious', 'no pulse', 'chest compressions']
    },
    {
        'id': 2,
        'title': 'Choking Relief (Heimlich Maneuver)',
        'description': 'Emergency procedure for airway obstruction',
        'icon': 'fas fa-lungs',
        'emergency_type': 'Airway Emergency',
        'image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/7CgtIgSyAiU',
        'duration': '2-5 minutes',
        'difficulty': 'Beginner',
        'keywords': ['choking', 'airway obstruction', 'heimlich', 'back blows', 'abdominal thrusts']
    },
    {
        'id': 3,
        'title': 'Burn Treatment',
        'description': 'Immediate care for thermal injuries',
        'icon': 'fas fa-fire',
        'emergency_type': 'Thermal Emergency',
        'image': 'https://images.unsplash.com/photo-1584515933487-779824d29309?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/kAOXABnbOns',
        'duration': '10-15 minutes',
        'difficulty': 'Beginner',
        'keywords': ['burns', 'thermal injury', 'fire', 'hot water', 'chemical burns', 'cooling']
    },
    {
        'id': 4,
        'title': 'Wound Care and Bleeding Control',
        'description': 'Managing cuts and severe bleeding',
        'icon': 'fas fa-band-aid',
        'emergency_type': 'Trauma Emergency',
        'image': 'https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/mFmNvyZhHtY',
        'duration': '5-10 minutes',
        'difficulty': 'Beginner',
        'keywords': ['bleeding', 'cuts', 'wounds', 'pressure', 'bandage', 'hemorrhage']
    },
    {
        'id': 5,
        'title': 'Fracture Management',
        'description': 'Stabilizing broken bones',
        'icon': 'fas fa-bone',
        'emergency_type': 'Orthopedic Emergency',
        'image': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/8BHXqQdWGf4',
        'duration': '10-20 minutes',
        'difficulty': 'Intermediate',
        'keywords': ['fracture', 'broken bone', 'splint', 'immobilization', 'support']
    },
    {
        'id': 6,
        'title': 'Shock Treatment',
        'description': 'Managing life-threatening shock',
        'icon': 'fas fa-exclamation-triangle',
        'emergency_type': 'Critical Emergency',
        'image': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/QvbHmGl7U8s',
        'duration': '5-15 minutes',
        'difficulty': 'Advanced',
        'keywords': ['shock', 'pale skin', 'weak pulse', 'low blood pressure', 'trauma']
    },
    {
        'id': 7,
        'title': 'Allergic Reaction Response',
        'description': 'Managing severe allergic reactions',
        'icon': 'fas fa-allergies',
        'emergency_type': 'Allergic Emergency',
        'image': 'https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/dXqbOOjRpzE',
        'duration': '3-10 minutes',
        'difficulty': 'Intermediate',
        'keywords': ['allergy', 'anaphylaxis', 'epipen', 'swelling', 'breathing difficulty']
    },
    {
        'id': 8,
        'title': 'Heat Stroke Treatment',
        'description': 'Managing heat-related emergencies',
        'icon': 'fas fa-thermometer-full',
        'emergency_type': 'Environmental Emergency',
        'image': 'https://images.unsplash.com/photo-1584515933487-779824d29309?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/7Bkn2d3F8yE',
        'duration': '10-20 minutes',
        'difficulty': 'Beginner',
        'keywords': ['heat stroke', 'overheating', 'dehydration', 'cooling', 'temperature']
    },
    {
        'id': 9,
        'title': 'Seizure Response',
        'description': 'How to help someone having a seizure',
        'icon': 'fas fa-brain',
        'emergency_type': 'Neurological Emergency',
        'image': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/WEkSYzeBb2c',
        'duration': '5-10 minutes',
        'difficulty': 'Beginner',
        'keywords': ['seizure', 'epilepsy', 'convulsions', 'safety', 'positioning']
    },
    {
        'id': 10,
        'title': 'Poisoning Emergency',
        'description': 'Immediate response to poisoning incidents',
        'icon': 'fas fa-skull-crossbones',
        'emergency_type': 'Toxicological Emergency',
        'image': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=400&h=300&fit=crop',
        'video_url': 'https://www.youtube.com/embed/QvbHmGl7U8s',
        'duration': '5-15 minutes',
        'difficulty': 'Intermediate',
        'keywords': ['poisoning', 'toxic', 'ingestion', 'chemicals', 'antidote']
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

@app.route('/medical-chatbot', methods=['GET', 'POST'])
@login_required
def medical_chatbot():
    if request.method == 'POST':
        data = request.get_json()
        user_message = data.get('message', '').strip().lower()

        # Simple AI-like responses for medical emergencies
        response = get_medical_emergency_response(user_message)
        return jsonify({'response': response})

    return render_template('medical_chatbot.html')

def get_medical_emergency_response(message):
    """Simple rule-based medical emergency chatbot responses"""

    # Emergency keywords and responses
    emergency_responses = {
        'heart attack': {
            'response': "🚨 **HEART ATTACK EMERGENCY** 🚨\n\n**IMMEDIATE ACTIONS:**\n1. Call 119 (ambulance) immediately\n2. Have the person sit down and rest\n3. Give aspirin if available and not allergic\n4. Loosen tight clothing\n5. Be ready to perform CPR if they become unconscious\n\n**SIGNS:** Chest pain, shortness of breath, nausea, sweating\n\n**DO NOT:** Give food or water",
            'urgency': 'critical'
        },
        'choking': {
            'response': "🚨 **CHOKING EMERGENCY** 🚨\n\n**IMMEDIATE ACTIONS:**\n1. Ask 'Are you choking?'\n2. If they can't speak/cough: Stand behind them\n3. Give 5 back blows between shoulder blades\n4. Give 5 abdominal thrusts (Heimlich maneuver)\n5. Alternate back blows and abdominal thrusts\n6. Call 118 if object doesn't dislodge\n\n**FOR INFANTS:** Use gentle back blows and chest thrusts",
            'urgency': 'critical'
        },
        'bleeding': {
            'response': "🩸 **BLEEDING CONTROL** 🩸\n\n**IMMEDIATE ACTIONS:**\n1. Apply direct pressure with clean cloth\n2. Elevate the injured area above heart level\n3. Don't remove embedded objects\n4. Apply pressure bandage\n5. Call 119 for severe bleeding\n\n**SEVERE BLEEDING SIGNS:** Spurting blood, won't stop after 10 minutes of pressure\n\n**SHOCK PREVENTION:** Keep person warm and lying down",
            'urgency': 'high'
        },
        'burn': {
            'response': "🔥 **BURN TREATMENT** 🔥\n\n**IMMEDIATE ACTIONS:**\n1. Remove from heat source safely\n2. Cool with running water for 10-20 minutes\n3. Remove jewelry/tight clothing before swelling\n4. Cover with clean, dry cloth\n5. Call 119 for severe burns\n\n**DO NOT:** Use ice, butter, or ointments\n**SEVERE BURNS:** Larger than palm, on face/hands/genitals, or deep",
            'urgency': 'high'
        },
        'fracture': {
            'response': "🦴 **FRACTURE MANAGEMENT** 🦴\n\n**IMMEDIATE ACTIONS:**\n1. Don't move the person unless in danger\n2. Support the injured area\n3. Apply splint if trained (don't move bone)\n4. Apply ice wrapped in cloth\n5. Call 119 for severe fractures\n\n**SIGNS:** Deformity, severe pain, inability to move, numbness\n**OPEN FRACTURE:** Don't push bone back in, cover with sterile dressing",
            'urgency': 'medium'
        },
        'seizure': {
            'response': "🧠 **SEIZURE RESPONSE** 🧠\n\n**IMMEDIATE ACTIONS:**\n1. Stay calm and time the seizure\n2. Clear area of dangerous objects\n3. Turn person on their side\n4. Put something soft under their head\n5. Call 119 if seizure lasts >5 minutes\n\n**DO NOT:** Put anything in their mouth, restrain them\n**AFTER SEIZURE:** Stay with them, they may be confused",
            'urgency': 'medium'
        },
        'poisoning': {
            'response': "☠️ **POISONING EMERGENCY** ☠️\n\n**IMMEDIATE ACTIONS:**\n1. Call Poison Control: 119\n2. Identify the poison if possible\n3. If conscious: rinse mouth with water\n4. Don't induce vomiting unless told to\n5. Save poison container/vomit sample\n\n**INHALED POISON:** Get to fresh air immediately\n**SKIN CONTACT:** Remove contaminated clothing, rinse with water",
            'urgency': 'critical'
        },
        'allergic reaction': {
            'response': "🤧 **ALLERGIC REACTION** 🤧\n\n**MILD REACTION:**\n- Antihistamine (Benadryl)\n- Cool compress for itching\n- Avoid allergen\n\n**SEVERE (ANAPHYLAXIS):**\n1. Call 119 immediately\n2. Use EpiPen if available\n3. Have person lie down, elevate legs\n4. Be ready for CPR\n\n**SIGNS OF ANAPHYLAXIS:** Difficulty breathing, swelling of face/throat, rapid pulse",
            'urgency': 'critical'
        },
        'unconscious': {
            'response': "😵 **UNCONSCIOUS PERSON** 😵\n\n**IMMEDIATE ACTIONS:**\n1. Check responsiveness: tap shoulders, shout\n2. Call 119 immediately\n3. Check breathing and pulse\n4. If breathing: recovery position\n5. If not breathing: start CPR\n\n**RECOVERY POSITION:** On side, head tilted back, top leg bent\n**CPR:** 30 chest compressions, 2 rescue breaths, repeat",
            'urgency': 'critical'
        },
        'cpr': {
            'response': "❤️ **CPR INSTRUCTIONS** ❤️\n\n**STEPS:**\n1. Check responsiveness and breathing\n2. Call 119\n3. Place heel of hand on center of chest\n4. Push hard and fast 2 inches deep\n5. 100-120 compressions per minute\n6. After 30 compressions: 2 rescue breaths\n7. Continue until help arrives\n\n**HAND POSITION:** Between nipples, fingers interlocked\n**DEPTH:** At least 2 inches for adults",
            'urgency': 'critical'
        }
    }

    # Check for emergency keywords
    for keyword, data in emergency_responses.items():
        if keyword in message or any(word in message for word in keyword.split()):
            return data['response']

    # General medical questions
    if any(word in message for word in ['pain', 'hurt', 'ache']):
        return "🩺 **PAIN MANAGEMENT** 🩺\n\nFor general pain:\n- Rest the affected area\n- Apply ice for injuries (20 min on/off)\n- Over-the-counter pain relievers if appropriate\n- Seek medical attention if severe or persistent\n\n**WHEN TO CALL 119:** Severe pain, chest pain, abdominal pain with fever, head injury pain"

    if any(word in message for word in ['fever', 'temperature', 'hot']):
        return "🌡️ **FEVER MANAGEMENT** 🌡️\n\n- Rest and stay hydrated\n- Light clothing\n- Cool compress on forehead\n- Fever reducers if appropriate\n\n**CALL 119 IF:** Fever >104°F (40°C), difficulty breathing, severe headache, stiff neck, confusion"

    if any(word in message for word in ['cut', 'wound', 'injury']):
        return "🩹 **WOUND CARE** 🩹\n\n**MINOR CUTS:**\n1. Clean hands first\n2. Stop bleeding with pressure\n3. Clean wound with water\n4. Apply antibiotic ointment\n5. Cover with bandage\n\n**SEEK MEDICAL CARE:** Deep cuts, won't stop bleeding, signs of infection, tetanus concerns"

    # Default response
    return """🤖 **MEDICAL EMERGENCY AI ASSISTANT** 🤖

I can help with emergency medical situations. Try asking about:

🚨 **EMERGENCIES:**
- Heart attack
- Choking
- Severe bleeding
- Burns
- Fractures
- Seizures
- Poisoning
- Allergic reactions
- Unconscious person
- CPR instructions

🩺 **GENERAL:**
- Pain management
- Fever treatment
- Wound care
- Basic first aid

**REMEMBER:** For life-threatening emergencies, call 119 immediately!

What medical emergency can I help you with?"""

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

