# 🚨 Emergency Response App - Complete Setup & Usage Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [API Endpoints Usage](#api-endpoints-usage)
3. [Prometheus & Grafana Setup](#prometheus--grafana-setup)
4. [Ansible Infrastructure as Code](#ansible-infrastructure-as-code)
5. [Testing & Validation](#testing--validation)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Ansible (for infrastructure automation)
- Git

### 1. Start the Emergency Response App
```bash
cd c:\Users\hp\Desktop\loopes\loope
python app.py
```

The app will be available at:
- **Main App**: http://127.0.0.1:3000
- **API Base**: http://127.0.0.1:3000/api/v1
- **Metrics**: http://127.0.0.1:3000/metrics

### 2. Test Login Credentials
- **Username**: `testuser`
- **Password**: `password123`
- **Fire Department**: `fireuser` / `password123`

---

## 🔌 API Endpoints Usage

### Authentication Required
Most endpoints require an API key in the header:
```bash
X-API-Key: emergency-api-key-2024
```

### Core Endpoints

#### 🏥 Health Check (No Auth Required)
```bash
curl http://127.0.0.1:3000/api/v1/health
```

#### 🔐 Authentication
```bash
# Login
curl -X POST http://127.0.0.1:3000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Register New User
curl -X POST http://127.0.0.1:3000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username":"newuser123",
    "email":"new123@test.com",
    "password":"password123",
    "full_name":"New User",
    "phone":"+237123456789",
    "user_type":"user"
  }'
```

#### 🚨 Emergency Reports
```bash
# Get All Emergencies
curl -H "X-API-Key: emergency-api-key-2024" \
  http://127.0.0.1:3000/api/v1/emergencies

# Create Emergency Report
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: emergency-api-key-2024" \
  -d '{
    "emergency_type":"fire",
    "location":"Downtown Yaoundé",
    "description":"Building fire on main street",
    "severity":"high",
    "latitude":3.8634,
    "longitude":11.5167,
    "user_id":1
  }' \
  http://127.0.0.1:3000/api/v1/emergencies

# Update Emergency Status
curl -X PUT \
  -H "Content-Type: application/json" \
  -H "X-API-Key: emergency-api-key-2024" \
  -d '{"status":"responding"}' \
  http://127.0.0.1:3000/api/v1/emergencies/1/status
```

#### 🚒 Fire Departments
```bash
curl -H "X-API-Key: emergency-api-key-2024" \
  http://127.0.0.1:3000/api/v1/fire-departments
```

#### 💬 Community Messages
```bash
# Get Messages
curl -H "X-API-Key: emergency-api-key-2024" \
  http://127.0.0.1:3000/api/v1/messages

# Create Message
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: emergency-api-key-2024" \
  -d '{
    "content":"Emergency update: Road blocked on Avenue Kennedy",
    "message_type":"alert",
    "user_id":1
  }' \
  http://127.0.0.1:3000/api/v1/messages
```

#### 🩺 First Aid Practices
```bash
# Get All First Aid Practices (No Auth Required)
curl http://127.0.0.1:3000/api/v1/first-aid

# Get Filtered Practices
curl "http://127.0.0.1:3000/api/v1/first-aid?category=Cardiac Emergency&difficulty=Intermediate"

# Get Specific Practice
curl http://127.0.0.1:3000/api/v1/first-aid/1
```

### 🧪 Automated API Testing
```bash
# Run comprehensive API tests
python test_api_endpoints.py

# Expected output: 90%+ success rate
```

### 📮 Postman Collection
Import `Emergency_Response_API.postman_collection.json` into Postman for GUI testing.

---

## 📊 Prometheus & Grafana Setup

### 1. Start Monitoring Stack
```bash
cd c:\Users\hp\Desktop\loopes\loope
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Access Monitoring Services

#### 📈 Prometheus (Metrics Collection)
- **URL**: http://localhost:9090
- **Purpose**: Collects metrics from the Emergency Response App
- **Key Metrics**:
  - `emergency_reports_total` - Total emergency reports by severity
  - `system_health_score` - System health (0-100)
  - `active_users` - Current active users
  - `first_aid_views_total` - First aid guide views

#### 📊 Grafana (Visualization Dashboard)
- **URL**: http://localhost:3001
- **Login**: `admin` / `emergency123`
- **Pre-configured Dashboard**: "Emergency Response App Dashboard"

**Dashboard Features**:
- Emergency Reports Rate (real-time)
- System Health Gauge
- Emergency Reports by Severity (pie chart)
- Active Users Counter
- Response Time Metrics

#### 🚨 Alertmanager (Alerts)
- **URL**: http://localhost:9093
- **Purpose**: Handles alerts from Prometheus

**Configured Alerts**:
- High Emergency Reports (>5 in 5 minutes)
- System Health Low (<50)
- App Down (>1 minute)
- High Response Time (>2 seconds)

### 3. Custom Metrics Queries

In Prometheus, try these queries:
```promql
# Emergency reports rate
rate(emergency_reports_total[5m])

# System health over time
system_health_score

# Active users
active_users

# HTTP request duration
flask_http_request_duration_seconds
```

### 4. Stop Monitoring Stack
```bash
docker-compose -f docker-compose.monitoring.yml down
```

---

## 🏗️ Ansible Infrastructure as Code

### Prerequisites
```bash
# Install Ansible (Ubuntu/Debian)
sudo apt update
sudo apt install ansible

# Install Ansible (Windows with WSL)
pip install ansible

# Install Ansible (macOS)
brew install ansible
```

### 1. Ansible Project Structure
```
ansible/
├── inventory.yml              # Server inventory
├── ansible.cfg              # Ansible configuration
├── site.yml                 # Master playbook
├── playbook-install-packages.yml    # Package installation
├── playbook-deploy-services.yml     # Service deployment
├── templates/               # Configuration templates
│   ├── emergency-app.service.j2
│   ├── nginx-emergency-app.conf.j2
│   ├── app-config.py.j2
│   ├── backup-script.sh.j2
│   └── emergency-app-logrotate.j2
└── run-playbooks.sh        # Execution script
```

### 2. Run Infrastructure Deployment

#### Option A: Automated Script
```bash
cd ansible
chmod +x run-playbooks.sh
./run-playbooks.sh
```

#### Option B: Manual Execution
```bash
cd ansible

# Check syntax
ansible-playbook --syntax-check site.yml

# Dry run
ansible-playbook --check site.yml

# Full deployment
ansible-playbook site.yml -v
```

### 3. Individual Playbooks

#### 📦 Package Installation Playbook
```bash
ansible-playbook playbook-install-packages.yml
```

**What it does**:
- Updates system packages
- Installs Python, pip, nginx, sqlite3
- Creates application user and directories
- Sets up Python virtual environment
- Configures firewall (UFW)
- Creates systemd service
- Configures nginx reverse proxy

#### 🚀 Service Deployment Playbook
```bash
ansible-playbook playbook-deploy-services.yml
```

**What it does**:
- Installs Docker and Docker Compose
- Deploys monitoring stack (Prometheus/Grafana)
- Copies application files
- Starts Emergency Response App service
- Sets up automated backups
- Configures log rotation
- Performs health checks

### 4. Ansible Inventory Configuration

Edit `ansible/inventory.yml` for your servers:
```yaml
all:
  hosts:
    production-server:
      ansible_host: your-server-ip
      ansible_user: ubuntu
      ansible_ssh_private_key_file: ~/.ssh/your-key.pem
    
    staging-server:
      ansible_host: staging-ip
      ansible_user: ubuntu
```

### 5. Ansible Execution Logs

The playbooks generate detailed logs:
```bash
# View execution logs
tail -f /var/log/ansible.log

# Check service status
sudo systemctl status emergency-app

# View application logs
sudo journalctl -u emergency-app -f
```

---

## ✅ Testing & Validation

### 1. Application Testing
```bash
# Test main application
curl http://localhost:3000

# Test API health
curl http://localhost:3000/api/v1/health

# Test metrics endpoint
curl http://localhost:3000/metrics
```

### 2. Monitoring Testing
```bash
# Test Prometheus
curl http://localhost:9090/api/v1/query?query=up

# Test Grafana API
curl -u admin:emergency123 http://localhost:3001/api/health
```

### 3. Service Status Checks
```bash
# Check all services
sudo systemctl status emergency-app nginx docker

# Check Docker containers
docker ps

# Check logs
sudo journalctl -u emergency-app --since "1 hour ago"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. App Won't Start
```bash
# Check Python dependencies
pip install -r requirements.txt

# Check database
python -c "from database import init_database; init_database()"

# Check port availability
netstat -tulpn | grep :3000
```

#### 2. Docker Issues
```bash
# Restart Docker
sudo systemctl restart docker

# Check Docker logs
docker-compose -f docker-compose.monitoring.yml logs

# Rebuild containers
docker-compose -f docker-compose.monitoring.yml up --build
```

#### 3. Ansible Issues
```bash
# Test connectivity
ansible all -m ping

# Check inventory
ansible-inventory --list

# Verbose execution
ansible-playbook site.yml -vvv
```

#### 4. API Issues
```bash
# Check API key
curl -H "X-API-Key: emergency-api-key-2024" http://localhost:3000/api/v1/status

# Test without auth
curl http://localhost:3000/api/v1/health

# Check app logs
tail -f /var/log/emergency-app/app.log
```

### Performance Optimization

#### 1. Database Optimization
```bash
# Backup database
cp emergency_app.db emergency_app.db.backup

# Vacuum database
sqlite3 emergency_app.db "VACUUM;"
```

#### 2. Monitoring Optimization
```bash
# Adjust Prometheus retention
# Edit monitoring/prometheus.yml
# Change --storage.tsdb.retention.time=200h
```

---

## 📞 Support & Resources

### Documentation Files
- `API_DOCUMENTATION.md` - Complete API reference
- `Emergency_Response_API.postman_collection.json` - Postman collection
- `test_api_endpoints.py` - Automated testing script

### Key URLs (When Running)
- **Main App**: http://127.0.0.1:3000
- **API Base**: http://127.0.0.1:3000/api/v1
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Alertmanager**: http://localhost:9093

### Emergency Contacts (In App)
- **Fire Rescue**: 118
- **Police**: 117
- **Ambulance**: 119

---

**🎉 Your Emergency Response App is now fully deployed with monitoring, infrastructure automation, and comprehensive API access!**
