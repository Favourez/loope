# 🚀 Emergency Response App - Setup Guide

## 📋 Overview

The `setup.sh` script provides automated installation and configuration for the Emergency Response App. It supports both local development and production deployment scenarios.

## 🎯 Quick Start

### Local Development Setup
```bash
# Basic setup for local development
./setup.sh

# Access your app at: http://localhost:3000
```

### Production Deployment
```bash
# Full production setup with monitoring
sudo ./setup.sh --production

# Access your app at: http://your-server-ip
```

## 📖 Usage Options

### Command Syntax
```bash
./setup.sh [OPTIONS]
```

### Available Options

| Option | Description |
|--------|-------------|
| `--docker` | Install Docker and Docker Compose |
| `--monitoring` | Start monitoring stack (Prometheus/Grafana) |
| `--production` | Full production setup (includes Docker and monitoring) |
| `--help` | Show help message |

### Usage Examples

#### 1. Basic Local Development
```bash
./setup.sh
```
**What it does:**
- Installs Python dependencies
- Sets up virtual environment
- Initializes SQLite database
- Starts the application locally

#### 2. Development with Docker
```bash
./setup.sh --docker
```
**What it does:**
- Everything from basic setup
- Installs Docker and Docker Compose
- Prepares for containerized services

#### 3. Development with Monitoring
```bash
./setup.sh --docker --monitoring
```
**What it does:**
- Everything from Docker setup
- Starts Prometheus and Grafana containers
- Configures monitoring dashboards

#### 4. Full Production Deployment
```bash
sudo ./setup.sh --production
```
**What it does:**
- Complete system setup
- Creates service user and directories
- Configures systemd services
- Sets up Nginx reverse proxy
- Configures firewall (UFW/firewalld)
- Installs Docker and monitoring stack
- Starts all services

## 🔧 Prerequisites

### System Requirements

#### Ubuntu/Debian
```bash
# Update system
sudo apt update

# Required for script execution
sudo apt install -y curl wget git
```

#### CentOS/RHEL
```bash
# Update system
sudo yum update -y

# Required for script execution
sudo yum install -y curl wget git
```

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Required tools
brew install curl wget git
```

### File Requirements
Ensure these files exist in your project directory:
- `app.py` (main application)
- `database.py` (database operations)
- `requirements.txt` (Python dependencies)
- `docker-compose.monitoring.yml` (monitoring stack)

## 🏗️ What the Script Does

### 1. System Dependencies Installation
- **Ubuntu/Debian**: `python3`, `python3-pip`, `python3-venv`, `git`, `nginx`, `sqlite3`, `curl`, `wget`, `ufw`
- **CentOS/RHEL**: `python3`, `python3-pip`, `git`, `nginx`, `sqlite`, `curl`, `wget`, `firewalld`
- **macOS**: `python3`, `git`, `nginx`, `sqlite3` (via Homebrew)

### 2. Application Setup
- Creates virtual environment
- Installs Python dependencies
- Initializes SQLite database with sample data
- Sets up proper file permissions

### 3. Production Configuration (with `--production`)
- Creates `emergency` system user
- Sets up systemd service for auto-start
- Configures Nginx reverse proxy
- Sets up firewall rules
- Creates log directories

### 4. Docker Installation (with `--docker`)
- Installs Docker CE
- Installs Docker Compose
- Starts Docker service
- Adds user to docker group

### 5. Monitoring Stack (with `--monitoring`)
- Starts Prometheus container
- Starts Grafana container
- Starts Alertmanager container
- Configures dashboards and data sources

## 🌐 Post-Installation Access

### Local Development
After running `./setup.sh`:
- **Main App**: http://localhost:3000
- **API Health**: http://localhost:3000/api/v1/health
- **Prometheus**: http://localhost:9090 (if `--monitoring` used)
- **Grafana**: http://localhost:3001 (if `--monitoring` used)

### Production Deployment
After running `sudo ./setup.sh --production`:
- **Main App**: http://your-server-ip
- **API Health**: http://your-server-ip/api/v1/health
- **Prometheus**: http://your-server-ip:9090
- **Grafana**: http://your-server-ip:3001

### Login Credentials
- **Regular User**: `testuser` / `password123`
- **Fire Department**: `fireuser` / `password123`
- **Grafana**: `admin` / `emergency123`

## 🔧 Management Commands

### Local Development
```bash
# Check if app is running
ps aux | grep python

# View application logs
tail -f app.log

# Stop application
kill $(cat app.pid)

# Restart application
./setup.sh
```

### Production Deployment
```bash
# Check service status
sudo systemctl status emergency-app nginx

# View application logs
sudo journalctl -u emergency-app -f

# Restart services
sudo systemctl restart emergency-app nginx

# Check monitoring containers
sudo docker ps

# Restart monitoring stack
cd /opt/emergency-app
sudo docker-compose -f docker-compose.monitoring.yml restart
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Make script executable
chmod +x setup.sh

# Run with sudo for production
sudo ./setup.sh --production
```

#### 2. Port Already in Use
```bash
# Check what's using port 3000
sudo netstat -tulpn | grep :3000

# Kill process if needed
sudo kill -9 <PID>
```

#### 3. Database Initialization Failed
```bash
# Check if database.py exists
ls -la database.py

# Manually initialize database
source venv/bin/activate
python -c "from database import init_database; init_database()"
```

#### 4. Nginx Configuration Error
```bash
# Test nginx configuration
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

#### 5. Docker Issues
```bash
# Check Docker service
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check container logs
sudo docker logs emergency-prometheus
sudo docker logs emergency-grafana
```

### Log Locations

#### Application Logs
- **Local**: `./app.log`
- **Production**: `sudo journalctl -u emergency-app`

#### System Logs
- **Nginx Access**: `/var/log/nginx/emergency-app-access.log`
- **Nginx Error**: `/var/log/nginx/emergency-app-error.log`
- **System**: `/var/log/syslog`

#### Container Logs
```bash
# View all container logs
sudo docker-compose -f docker-compose.monitoring.yml logs

# View specific container logs
sudo docker logs emergency-prometheus
sudo docker logs emergency-grafana
sudo docker logs emergency-alertmanager
```

## 🔄 Updating the Application

### Local Development
```bash
# Pull latest changes
git pull

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart application
kill $(cat app.pid)
./setup.sh
```

### Production Deployment
```bash
# Pull latest changes
cd /opt/emergency-app
sudo git pull

# Update dependencies
sudo -u emergency bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Restart services
sudo systemctl restart emergency-app nginx
```

## 🚀 Advanced Configuration

### Custom VPS Configuration
Edit the script variables at the top of `setup.sh`:
```bash
# VPS Configuration
VPS_HOST="your-vps-ip"
VPS_HOSTNAME="your-hostname.com"
VPS_USER="root"
```

### Custom Ports
To change default ports, modify:
- Application port: Edit `app.py` (default: 3000)
- Prometheus port: Edit `docker-compose.monitoring.yml` (default: 9090)
- Grafana port: Edit `docker-compose.monitoring.yml` (default: 3001)

### SSL/HTTPS Setup
After basic setup, configure SSL:
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review log files for error messages
3. Ensure all prerequisites are met
4. Verify file permissions and ownership

**🎉 Your Emergency Response App setup is now complete and ready to help save lives!**
