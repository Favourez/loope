from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

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
    return render_template('welcome.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/map')
def map_page():
    return render_template('map.html')

@app.route('/messages')
def messages():
    return render_template('messages.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/first-aid')
def first_aid():
    return render_template('first_aid.html', practices=FIRST_AID_PRACTICES)

@app.route('/first-aid/<int:practice_id>')
def first_aid_detail(practice_id):
    practice = next((p for p in FIRST_AID_PRACTICES if p['id'] == practice_id), None)
    if not practice:
        return redirect(url_for('first_aid'))
    return render_template('first_aid_detail.html', practice=practice)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/guidelines')
def guidelines():
    return render_template('guidelines.html')

@app.route('/report-emergency', methods=['POST'])
def report_emergency():
    data = request.get_json()
    # Here you would typically save to database
    # For now, we'll just return a success response
    return jsonify({'status': 'success', 'message': 'Emergency reported successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
