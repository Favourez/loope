# 🏗️ Ansible Infrastructure as Code - Detailed Execution Guide

## 📋 Overview
This guide provides step-by-step instructions for deploying the Emergency Response App infrastructure using Ansible automation.

## 🎯 What Ansible Will Deploy

### Infrastructure Components
1. **Web Server Setup**
   - Nginx reverse proxy
   - SSL/TLS configuration
   - Firewall rules (UFW)
   - Log rotation

2. **Application Environment**
   - Python 3.8+ with virtual environment
   - Flask application with dependencies
   - SQLite database
   - Systemd service configuration

3. **Monitoring Stack**
   - Docker & Docker Compose
   - Prometheus metrics collection
   - Grafana dashboards
   - Alertmanager notifications

4. **Security & Maintenance**
   - Automated backups
   - Log management
   - Security headers
   - Process monitoring

## 🚀 Step-by-Step Execution

### Step 1: Prerequisites Check
```bash
# Check Ansible installation
ansible --version

# Expected output:
# ansible [core 2.12.x]
# python version = 3.x.x

# If not installed:
# Ubuntu/Debian: sudo apt install ansible
# CentOS/RHEL: sudo yum install ansible
# macOS: brew install ansible
# Windows: pip install ansible
```

### Step 2: Prepare Inventory
```bash
cd ansible

# Edit inventory.yml for your target servers
nano inventory.yml
```

**Example inventory.yml**:
```yaml
all:
  hosts:
    emergency-app-server:
      ansible_host: 192.168.1.100  # Your server IP
      ansible_user: ubuntu         # SSH user
      ansible_ssh_private_key_file: ~/.ssh/emergency-app-key.pem
  
  children:
    web_servers:
      hosts:
        emergency-app-server:
      vars:
        app_name: emergency-response-app
        app_port: 3000
        app_user: emergency
        app_directory: /opt/emergency-app
```

### Step 3: Test Connectivity
```bash
# Test SSH connectivity to all hosts
ansible all -m ping

# Expected output:
# emergency-app-server | SUCCESS => {
#     "ansible_facts": {
#         "discovered_interpreter_python": "/usr/bin/python3"
#     },
#     "changed": false,
#     "ping": "pong"
# }
```

### Step 4: Syntax Validation
```bash
# Check playbook syntax
ansible-playbook --syntax-check site.yml

# Expected output:
# playbook: site.yml

# Check individual playbooks
ansible-playbook --syntax-check playbook-install-packages.yml
ansible-playbook --syntax-check playbook-deploy-services.yml
```

### Step 5: Dry Run (Check Mode)
```bash
# Perform dry run to see what would change
ansible-playbook --check site.yml

# This shows what Ansible would do without making changes
# Look for:
# - TASK [task_name] ****
# - changed: [server_name]
# - ok: [server_name]
```

### Step 6: Execute Package Installation
```bash
# Run first playbook: Install packages and dependencies
ansible-playbook playbook-install-packages.yml -v

# Monitor output for:
# ✅ Package installations
# ✅ User creation
# ✅ Directory setup
# ✅ Virtual environment creation
# ✅ Firewall configuration
# ✅ Nginx setup
```

**Expected Output Sections**:
```
TASK [Update package cache (Ubuntu/Debian)] ****
changed: [emergency-app-server]

TASK [Install system packages (Ubuntu/Debian)] ****
changed: [emergency-app-server] => (item=['python3', 'python3-pip', ...])

TASK [Create application user] ****
changed: [emergency-app-server]

TASK [Create Python virtual environment] ****
changed: [emergency-app-server]

TASK [Configure UFW firewall] ****
changed: [emergency-app-server] => (item=3000)
changed: [emergency-app-server] => (item=22)

PLAY RECAP ****
emergency-app-server : ok=15 changed=12 unreachable=0 failed=0
```

### Step 7: Execute Service Deployment
```bash
# Run second playbook: Deploy services and monitoring
ansible-playbook playbook-deploy-services.yml -v

# Monitor output for:
# ✅ Docker installation
# ✅ Application file deployment
# ✅ Monitoring stack startup
# ✅ Service activation
# ✅ Health checks
```

**Expected Output Sections**:
```
TASK [Install Docker] ****
changed: [emergency-app-server]

TASK [Start monitoring services with Docker Compose] ****
changed: [emergency-app-server]

TASK [Start emergency app service] ****
changed: [emergency-app-server]

TASK [Test application health] ****
ok: [emergency-app-server]

TASK [Display health check result] ****
ok: [emergency-app-server] => {
    "msg": "Application health check: {'status': 'healthy'}"
}

PLAY RECAP ****
emergency-app-server : ok=18 changed=14 unreachable=0 failed=0
```

### Step 8: Full Deployment (Alternative)
```bash
# Run complete deployment with master playbook
ansible-playbook site.yml -v

# This runs both playbooks in sequence
# Equivalent to running steps 6 and 7 together
```

## 📊 Execution Logs & Screenshots

### Log Locations
```bash
# Ansible execution logs
tail -f /var/log/ansible.log

# Application service logs
sudo journalctl -u emergency-app -f

# Nginx access logs
sudo tail -f /var/log/nginx/emergency-app-access.log

# Docker container logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Service Status Verification
```bash
# Check all services after deployment
sudo systemctl status emergency-app nginx docker

# Check Docker containers
docker ps

# Expected containers:
# - emergency-prometheus
# - emergency-grafana
# - emergency-alertmanager
# - emergency-node-exporter
```

### Application Health Checks
```bash
# Test application endpoints
curl http://localhost:3000/api/v1/health
curl http://localhost:3000/metrics

# Test monitoring services
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3001/api/health # Grafana
```

## 🔧 Troubleshooting Ansible Execution

### Common Issues & Solutions

#### 1. SSH Connection Issues
```bash
# Problem: SSH connection failed
# Solution: Check SSH key and connectivity
ssh -i ~/.ssh/your-key.pem ubuntu@your-server-ip

# Verify SSH agent
ssh-add ~/.ssh/your-key.pem
```

#### 2. Permission Denied
```bash
# Problem: Permission denied for sudo operations
# Solution: Ensure user has sudo privileges
ansible all -m shell -a "sudo whoami" --ask-become-pass
```

#### 3. Package Installation Failures
```bash
# Problem: Package installation failed
# Solution: Update package cache manually
ansible all -m apt -a "update_cache=yes" --become
```

#### 4. Docker Issues
```bash
# Problem: Docker service won't start
# Solution: Check Docker installation
ansible all -m shell -a "sudo systemctl status docker" --become
```

#### 5. Application Won't Start
```bash
# Problem: Emergency app service failed
# Solution: Check application logs
ansible all -m shell -a "sudo journalctl -u emergency-app --no-pager" --become
```

## 📈 Monitoring Deployment Success

### Key Metrics to Verify
1. **Service Status**: All systemd services running
2. **Port Accessibility**: Ports 3000, 9090, 3001 accessible
3. **Health Endpoints**: API health checks passing
4. **Log Generation**: Application generating logs
5. **Metrics Collection**: Prometheus collecting metrics

### Verification Commands
```bash
# Service status
ansible all -m shell -a "sudo systemctl is-active emergency-app nginx docker"

# Port checks
ansible all -m shell -a "netstat -tulpn | grep -E ':(3000|9090|3001)'"

# Health checks
ansible all -m uri -a "url=http://localhost:3000/api/v1/health"

# Log verification
ansible all -m shell -a "sudo tail -5 /var/log/emergency-app/app.log"
```

## 🔄 Rerunning Playbooks

### Idempotent Operations
Ansible playbooks are idempotent - safe to run multiple times:
```bash
# Rerun to ensure desired state
ansible-playbook site.yml

# Update specific components
ansible-playbook playbook-install-packages.yml --tags "nginx,firewall"
```

### Selective Execution
```bash
# Run only specific tasks
ansible-playbook site.yml --tags "application"

# Skip certain tasks
ansible-playbook site.yml --skip-tags "docker"

# Target specific hosts
ansible-playbook site.yml --limit "emergency-app-server"
```

## 📝 Execution Checklist

### Pre-Execution
- [ ] Ansible installed and configured
- [ ] SSH connectivity to target servers
- [ ] Inventory file updated with correct IPs
- [ ] SSH keys properly configured
- [ ] Target servers have sudo access

### During Execution
- [ ] Monitor output for errors
- [ ] Verify each task completion
- [ ] Check for "failed=0" in PLAY RECAP
- [ ] Note any warnings or skipped tasks

### Post-Execution
- [ ] All services running (systemctl status)
- [ ] Application accessible (curl tests)
- [ ] Monitoring stack operational
- [ ] Logs being generated
- [ ] Backup scripts scheduled
- [ ] Firewall rules applied

## 🎯 Expected Results

### Successful Deployment Indicators
1. **Zero Failed Tasks**: PLAY RECAP shows "failed=0"
2. **Services Running**: emergency-app, nginx, docker active
3. **Ports Open**: 3000, 9090, 3001 accessible
4. **Health Checks Pass**: API returns 200 status
5. **Monitoring Active**: Prometheus collecting metrics
6. **Logs Generated**: Application writing to log files

### Performance Benchmarks
- **Deployment Time**: 5-10 minutes for full stack
- **Service Start Time**: <30 seconds for application
- **Health Check Response**: <2 seconds
- **Memory Usage**: <512MB for application
- **Disk Usage**: <2GB for full installation

---

**🎉 Your infrastructure is now fully automated and deployed using Ansible!**

The Emergency Response App is running with:
- ✅ Automated package management
- ✅ Service configuration
- ✅ Monitoring stack
- ✅ Security hardening
- ✅ Backup automation
- ✅ Log management
