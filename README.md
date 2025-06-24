# 🚨 Emergency Response App - Complete Documentation

## 📋 Project Overview

A comprehensive Emergency Response Application for Cameroon with dual user registration, AI-powered medical assistance, smart pathfinding, and real-time monitoring.

### 🎯 Key Features
- **Dual Registration System**: Regular users and Fire Department users
- **Enhanced Map**: Smart pathfinding with Dijkstra's algorithm to hospitals/fire stations
- **AI Medical Chatbot**: Pre-trained for medical emergency questions
- **First Aid Guides**: 10 practices with professional images and training videos
- **Real-time Monitoring**: Prometheus & Grafana dashboards
- **Comprehensive API**: 18 RESTful endpoints
- **Infrastructure as Code**: Ansible automation

---

## 🌐 Live Application

### **Production URLs**
- **Main App**: http://31.97.11.49
- **Main App**: http://srv878357.hstgr.cloud
- **API Health**: http://31.97.11.49/api/v1/health
- **Prometheus**: http://31.97.11.49:9090
- **Grafana**: http://31.97.11.49:3001

### **Login Credentials**
- **Regular User**: `testuser` / `password123`
- **Fire Department**: `fireuser` / `password123`
- **Grafana**: `admin` / `emergency123` (or `admin` / `admin`)

---

## 🚀 Quick Start

### Automated Setup (Recommended)
```bash
# Make setup script executable
chmod +x setup.sh

# Local development setup
./setup.sh

# Production deployment (requires sudo)
sudo ./setup.sh --production

# Development with monitoring
./setup.sh --docker --monitoring
```

### Manual Installation
```bash
# Clone or download the project
cd emergency-response-app

# Install dependencies
pip install -r requirements.txt

# Initialize database (first time only)
python -c "from database import init_database; init_database()"
```

### Local Development
```bash
# Start the application
python app.py

# Access locally
http://127.0.0.1:3000
```

### Start Monitoring Stack
```bash
# Start Prometheus & Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# Access monitoring
# Grafana: http://localhost:3001
# Prometheus: http://localhost:9090
```

---

## 🔌 API Documentation

### Base URL
```
Production: http://31.97.11.49/api/v1
Local: http://127.0.0.1:3000/api/v1
```

### Authentication
Include API key in header:
```
X-API-Key: emergency-api-key-2024
```

### Core Endpoints

#### Health Check (No Auth)
```bash
GET /health
curl http://93.127.214.57/api/v1/health
```

#### Authentication
```bash
# Login
POST /auth/login
{
  "username": "testuser",
  "password": "password123"
}

# Register
POST /auth/register
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "New User",
  "phone": "+237123456789"
}
```

#### Emergency Reports
```bash
# Get all emergencies
GET /emergencies
curl -H "X-API-Key: emergency-api-key-2024" \
  http://31.97.11.49/api/v1/emergencies

# Create emergency
POST /emergencies
{
  "emergency_type": "fire",
  "location": "Yaoundé Center",
  "description": "Building fire",
  "severity": "high",
  "latitude": 3.8634,
  "longitude": 11.5167
}

# Update status
PUT /emergencies/{id}/status
{
  "status": "responding"
}
```

#### First Aid Practices
```bash
# Get all practices
GET /first-aid

# Get specific practice
GET /first-aid/{id}

# Filter by category
GET /first-aid?category=Cardiac Emergency&difficulty=Intermediate
```

#### Fire Departments & Messages
```bash
# Get fire departments
GET /fire-departments

# Get messages
GET /messages

# Create message
POST /messages
{
  "content": "Emergency update",
  "message_type": "alert"
}
```

---

## 🎮 Application Features

### 1. Enhanced Map System
- **Smart Pathfinding**: Dijkstra's algorithm for optimal routes
- **Multiple Arrows**: Shows top 5 nearest hospitals/fire stations
- **Distance Labels**: Exact distances with "NEAREST" indicator
- **Visual Hierarchy**: Color-coded arrows and ranking

### 2. AI Medical Assistant
- **Emergency Recognition**: Responds to "heart attack", "choking", "burns", etc.
- **Step-by-Step Instructions**: Detailed emergency procedures
- **Quick Buttons**: One-click access to common emergencies
- **Emergency Call Integration**: Direct 119 calling

### 3. First Aid Guides
- **10 Medical Practices**: CPR, Choking, Burns, Bleeding, Fractures, etc.
- **Professional Images**: High-quality medical emergency photos
- **Training Videos**: Real YouTube educational content
- **Difficulty Levels**: Beginner, Intermediate, Advanced
- **Interactive Learning**: Images, videos, and AI assistance

### 4. Dual User System
- **Regular Users**: Emergency reporting and community features
- **Fire Departments**: Specialized dashboard and response tools
- **Separate Landing Pages**: Customized interfaces per user type

---

## 📊 Monitoring & Analytics

### Grafana Dashboard
Access: http://31.97.11.49:3001 (admin/emergency123)

**Key Metrics:**
- Emergency Reports Rate (real-time)
- System Health Score (0-100)
- Active Users Count
- Response Time Metrics

### Prometheus Metrics
Access: http://31.97.11.49:9090

**Available Metrics:**
```promql
# Emergency reports by severity
emergency_reports_total{severity="high"}

# System health indicator
system_health_score

# Active users
active_users

# First aid guide views
first_aid_views_total

# HTTP request metrics
flask_http_request_total
flask_http_request_duration_seconds
```

### Custom Queries
```promql
# Emergency reports rate
rate(emergency_reports_total[5m])

# Response time 95th percentile
histogram_quantile(0.95, flask_http_request_duration_seconds_bucket)

# Page views by type
page_views_total{page="landing"}
```

---

## 🏗️ Infrastructure & Deployment

### VPS Configuration
- **Server**: 31.97.11.49 (srv878357.hstgr.cloud)
- **OS**: Ubuntu/Debian
- **Services**: Nginx, Python, Docker, UFW Firewall

### Deployed Services
- **emergency-app.service**: Main application (systemd)
- **nginx**: Reverse proxy and web server
- **docker**: Container management for monitoring
- **ufw**: Firewall (ports 22, 80, 443, 3000, 9090, 3001, 9093)

### Ansible Automation
```bash
# Deploy infrastructure
cd ansible
ansible-playbook site.yml

# Individual playbooks
ansible-playbook playbook-install-packages.yml
ansible-playbook playbook-deploy-services.yml
```

---

## 🔧 Management & Maintenance

### Service Management
```bash
# SSH to VPS
ssh root@31.97.11.49

# Check service status
systemctl status emergency-app nginx docker

# Restart services
systemctl restart emergency-app
systemctl reload nginx

# View logs
journalctl -u emergency-app -f
tail -f /var/log/nginx/emergency-app-access.log
```

### Docker Management
```bash
# Check containers
docker ps

# Restart monitoring stack
cd /opt/emergency-app
docker-compose -f docker-compose.monitoring.yml restart

# View container logs
docker logs emergency-grafana
docker logs emergency-prometheus
```

### Database Management
```bash
# Backup database
cp /opt/emergency-app/emergency_app.db backup_$(date +%Y%m%d).db

# Check database
sqlite3 /opt/emergency-app/emergency_app.db ".tables"
```

---

## 🔄 CI/CD Pipeline

### Automated Deployment
The project includes comprehensive CI/CD pipelines for automated testing and deployment:

#### Jenkins Pipeline (`Jenkinsfile`)
- **Multi-stage pipeline** with build, test, and deployment
- **Parallel execution** for faster builds
- **Security scanning** with Bandit and Safety
- **Docker integration** for containerized deployments
- **Blue-green deployment** support
- **Automatic rollback** on failure

#### GitHub Actions (`.github/workflows/ci-cd.yml`)
- **Matrix testing** across Python versions
- **Automated testing** on push and pull requests
- **Docker image building** and publishing
- **Staging and production deployments**
- **Integration testing** against live environments

#### Pipeline Features
- ✅ **Code Quality**: Linting, formatting, security scans
- ✅ **Testing**: Unit tests, integration tests, performance tests
- ✅ **Building**: Application packaging, Docker images
- ✅ **Deployment**: Staging and production environments
- ✅ **Monitoring**: Health checks, performance verification
- ✅ **Notifications**: Email and Slack alerts

#### Setup Instructions
```bash
# For Jenkins
# See CI_CD_SETUP.md for complete Jenkins setup

# For GitHub Actions
# Configure secrets in repository settings:
# - DOCKER_USERNAME, DOCKER_PASSWORD
# - STAGING_SSH_KEY, PROD_SSH_KEY
# - EMAIL_USERNAME, EMAIL_PASSWORD
# - SLACK_WEBHOOK_URL
```

---

## 🧪 Testing

### API Testing with Postman
1. Import: `Emergency_Response_API.postman_collection.json`
2. Set environment variables:
   - `base_url`: http://31.97.11.49/api/v1
   - `api_key`: emergency-api-key-2024
3. Test all endpoints

### Manual Testing
```bash
# Health check
curl http://31.97.11.49/api/v1/health

# Create emergency with API key
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: emergency-api-key-2024" \
  -d '{"emergency_type":"test","location":"Test","description":"Test","severity":"medium"}' \
  http://31.97.11.49/api/v1/emergencies

# Test monitoring
curl http://31.97.11.49:9090/-/healthy
curl http://31.97.11.49:3001/api/health
```

---

## 🔒 Security

### Firewall Configuration
- **Port 22**: SSH access
- **Port 80**: HTTP traffic
- **Port 443**: HTTPS traffic (ready for SSL)
- **Port 3000**: Application (internal)
- **Ports 9090, 3001, 9093**: Monitoring services

### Security Headers
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: 1; mode=block
- X-Content-Type-Options: nosniff
- Content Security Policy configured

### API Security
- API key authentication required
- Rate limiting ready for implementation
- Input validation and sanitization

---

## 📁 Project Structure

```
emergency-response-app/
├── setup.sh                        # 🚀 Automated setup script
├── SETUP_GUIDE.md                  # 📖 Setup script documentation
├── Jenkinsfile                     # 🔄 Jenkins CI/CD pipeline
├── CI_CD_SETUP.md                  # 📋 CI/CD documentation
├── app.py                          # Main Flask application
├── database.py                     # Database operations
├── auth.py                         # Authentication system
├── api_endpoints.py                # RESTful API endpoints
├── emergency_app.db                # SQLite database
├── requirements.txt                # Python dependencies
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── landing.html                # Main landing page
│   ├── fire_department_landing.html # Fire dept dashboard
│   ├── first_aid.html              # First aid practices
│   ├── first_aid_detail.html       # Detailed first aid guide
│   ├── medical_chatbot.html        # AI medical assistant
│   ├── map.html                    # Enhanced map with pathfinding
│   ├── messages.html               # Community messaging
│   ├── profile.html                # User profile management
│   └── ...                        # Other templates
├── static/                         # Static assets
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript files
│   ├── images/                     # Images and icons
│   └── videos/                     # Video content
├── monitoring/                     # Monitoring configuration
│   ├── prometheus.yml              # Prometheus config
│   ├── alertmanager.yml            # Alert manager config
│   ├── alert_rules.yml             # Alert rules
│   └── grafana/                    # Grafana dashboards
├── tests/                          # Test suite
│   ├── test_app.py                 # Unit tests
│   ├── integration/                # Integration tests
│   └── pytest.ini                 # Test configuration
├── .github/workflows/              # GitHub Actions CI/CD
│   └── ci-cd.yml                   # Automated pipeline
├── ansible/                        # Infrastructure as Code
│   ├── site.yml                    # Master playbook
│   ├── playbook-install-packages.yml # Package installation
│   ├── playbook-deploy-services.yml  # Service deployment
│   ├── inventory.yml               # Server inventory
│   ├── ansible.cfg                 # Ansible configuration
│   └── templates/                  # Configuration templates
├── docker-compose.monitoring.yml   # Monitoring stack
├── Emergency_Response_API.postman_collection.json # API testing
└── README.md                       # Complete documentation
```

---

## 🆘 Emergency Contacts (In App)

- **Fire Rescue**: 118
- **Police**: 117
- **Ambulance**: 119

---

## 🎉 Success Metrics

### Deployment Status: ✅ COMPLETED
- **Application**: Live at http://31.97.11.49
- **API Success Rate**: 100% (8/8 endpoints working)
- **Monitoring**: Operational with Prometheus & Grafana
- **Infrastructure**: Fully automated with Ansible
- **Features**: All core features implemented and working

### Key Achievements
- ✅ Dual registration system with separate user flows
- ✅ Enhanced map with smart pathfinding (Dijkstra's algorithm)
- ✅ AI medical chatbot with emergency recognition
- ✅ First aid guides with images and videos
- ✅ 18 RESTful API endpoints
- ✅ Real-time monitoring and alerting
- ✅ Production deployment on VPS
- ✅ Infrastructure as Code with Ansible

---

## 📞 Support

For technical issues or questions:
1. Check service status: `systemctl status emergency-app`
2. View logs: `journalctl -u emergency-app -f`
3. Test API health: `curl http://31.97.11.49/api/v1/health`
4. Access monitoring: http://31.97.11.49:3001

**🚑 Your Emergency Response App is live and ready to help save lives! 🌍**
