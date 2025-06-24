#!/bin/bash

# Emergency Response App - Complete Setup Script
# This script sets up the entire Emergency Response App environment
# Supports both local development and production deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Emergency Response App"
PROJECT_DIR="/opt/emergency-app"
SERVICE_USER="emergency"
PYTHON_VERSION="3.12"
VENV_NAME="venv"

# VPS Configuration (update these for your VPS)
VPS_HOST="31.97.11.49"
VPS_HOSTNAME="srv878357.hstgr.cloud"
VPS_USER="root"

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
        elif command -v yum &> /dev/null; then
            OS="centos"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_status "Detected OS: $OS"
}

# Install system dependencies
install_system_deps() {
    print_header "INSTALLING SYSTEM DEPENDENCIES"
    
    case $OS in
        "ubuntu")
            print_status "Updating package cache..."
            apt update
            
            print_status "Installing system packages..."
            DEBIAN_FRONTEND=noninteractive apt install -y \
                python3 \
                python3-pip \
                python3-venv \
                python3-dev \
                git \
                nginx \
                sqlite3 \
                curl \
                wget \
                unzip \
                htop \
                vim \
                ufw \
                build-essential \
                software-properties-common
            ;;
        "centos")
            print_status "Installing system packages..."
            yum update -y
            yum install -y \
                python3 \
                python3-pip \
                python3-devel \
                git \
                nginx \
                sqlite \
                curl \
                wget \
                unzip \
                htop \
                vim \
                firewalld \
                gcc \
                gcc-c++
            ;;
        "macos")
            print_status "Installing system packages via Homebrew..."
            if ! command -v brew &> /dev/null; then
                print_status "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python3 git nginx sqlite3 curl wget
            ;;
        *)
            print_warning "Unsupported OS. Please install dependencies manually."
            ;;
    esac
    
    print_success "System dependencies installed!"
}

# Create application user (Linux only)
create_app_user() {
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "centos" ]]; then
        print_header "CREATING APPLICATION USER"
        
        if id "$SERVICE_USER" &>/dev/null; then
            print_warning "User $SERVICE_USER already exists"
        else
            print_status "Creating user: $SERVICE_USER"
            useradd -r -s /bin/bash -d $PROJECT_DIR $SERVICE_USER
            print_success "User $SERVICE_USER created"
        fi
        
        print_status "Creating directories..."
        mkdir -p $PROJECT_DIR
        mkdir -p /var/log/emergency-app
        
        if check_root; then
            chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
            chown $SERVICE_USER:$SERVICE_USER /var/log/emergency-app
        fi
        
        print_success "Directories created and permissions set"
    fi
}

# Setup Python environment
setup_python_env() {
    print_header "SETTING UP PYTHON ENVIRONMENT"
    
    # Determine working directory
    if [[ -d "$PROJECT_DIR" ]] && check_root; then
        WORK_DIR="$PROJECT_DIR"
    else
        WORK_DIR="$(pwd)"
    fi
    
    print_status "Working directory: $WORK_DIR"
    cd "$WORK_DIR"
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv $VENV_NAME
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source $VENV_NAME/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing Python dependencies from requirements.txt..."
        pip install -r requirements.txt
    else
        print_status "Installing Python dependencies manually..."
        pip install \
            Flask==2.3.3 \
            Flask-Login==0.6.3 \
            prometheus-client==0.17.1 \
            prometheus-flask-exporter==0.23.0 \
            bcrypt==4.0.1 \
            email-validator==2.0.0
    fi
    
    print_success "Python environment setup complete!"
}

# Initialize database
init_database() {
    print_header "INITIALIZING DATABASE"
    
    # Determine working directory
    if [[ -d "$PROJECT_DIR" ]] && check_root; then
        WORK_DIR="$PROJECT_DIR"
    else
        WORK_DIR="$(pwd)"
    fi
    
    cd "$WORK_DIR"
    
    if [[ -f "database.py" ]]; then
        print_status "Initializing SQLite database..."
        source $VENV_NAME/bin/activate
        python -c "from database import init_database; init_database()"
        print_success "Database initialized successfully!"
    else
        print_warning "database.py not found. Skipping database initialization."
    fi
}

# Setup systemd service (Linux only)
setup_systemd_service() {
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "centos" ]]; then
        if check_root; then
            print_header "SETTING UP SYSTEMD SERVICE"
            
            print_status "Creating systemd service file..."
            cat > /etc/systemd/system/emergency-app.service << EOF
[Unit]
Description=Emergency Response App
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/$VENV_NAME/bin
ExecStart=$PROJECT_DIR/$VENV_NAME/bin/python app.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=emergency-app

[Install]
WantedBy=multi-user.target
EOF
            
            print_status "Reloading systemd daemon..."
            systemctl daemon-reload
            
            print_status "Enabling emergency-app service..."
            systemctl enable emergency-app
            
            print_success "Systemd service configured!"
        else
            print_warning "Root privileges required for systemd service setup"
        fi
    fi
}

# Configure Nginx
configure_nginx() {
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "centos" ]]; then
        if check_root; then
            print_header "CONFIGURING NGINX"
            
            print_status "Creating Nginx configuration..."
            cat > /etc/nginx/sites-available/emergency-app << EOF
server {
    listen 80;
    server_name $VPS_HOSTNAME $VPS_HOST localhost;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /metrics {
        proxy_pass http://127.0.0.1:3000/metrics;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Logging
    access_log /var/log/nginx/emergency-app-access.log;
    error_log /var/log/nginx/emergency-app-error.log;
}
EOF
            
            # Enable site
            if [[ -d "/etc/nginx/sites-enabled" ]]; then
                print_status "Enabling Nginx site..."
                ln -sf /etc/nginx/sites-available/emergency-app /etc/nginx/sites-enabled/
                rm -f /etc/nginx/sites-enabled/default
            fi
            
            print_status "Testing Nginx configuration..."
            nginx -t
            
            print_status "Enabling and starting Nginx..."
            systemctl enable nginx
            systemctl reload nginx
            
            print_success "Nginx configured successfully!"
        else
            print_warning "Root privileges required for Nginx configuration"
        fi
    fi
}

# Configure firewall
configure_firewall() {
    if [[ "$OS" == "ubuntu" ]] && check_root; then
        print_header "CONFIGURING FIREWALL"
        
        print_status "Configuring UFW firewall..."
        ufw --force reset
        ufw default deny incoming
        ufw default allow outgoing
        
        # Allow necessary ports
        ufw allow 22      # SSH
        ufw allow 80      # HTTP
        ufw allow 443     # HTTPS
        ufw allow 3000    # Emergency App
        ufw allow 9090    # Prometheus
        ufw allow 3001    # Grafana
        ufw allow 9093    # Alertmanager
        
        ufw --force enable
        
        print_success "Firewall configured!"
    elif [[ "$OS" == "centos" ]] && check_root; then
        print_header "CONFIGURING FIREWALL"
        
        print_status "Configuring firewalld..."
        systemctl enable firewalld
        systemctl start firewalld
        
        # Allow necessary ports
        firewall-cmd --permanent --add-port=22/tcp
        firewall-cmd --permanent --add-port=80/tcp
        firewall-cmd --permanent --add-port=443/tcp
        firewall-cmd --permanent --add-port=3000/tcp
        firewall-cmd --permanent --add-port=9090/tcp
        firewall-cmd --permanent --add-port=3001/tcp
        firewall-cmd --permanent --add-port=9093/tcp
        
        firewall-cmd --reload
        
        print_success "Firewall configured!"
    fi
}

# Install Docker
install_docker() {
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "centos" ]]; then
        if check_root; then
            print_header "INSTALLING DOCKER"
            
            print_status "Installing Docker..."
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            
            print_status "Installing Docker Compose..."
            curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
            
            print_status "Starting Docker service..."
            systemctl enable docker
            systemctl start docker
            
            # Add user to docker group if not root
            if [[ -n "$SUDO_USER" ]]; then
                usermod -aG docker $SUDO_USER
            fi
            
            print_success "Docker installed successfully!"
        else
            print_warning "Root privileges required for Docker installation"
        fi
    fi
}

# Start services
start_services() {
    if check_root && ([[ "$OS" == "ubuntu" ]] || [[ "$OS" == "centos" ]]); then
        print_header "STARTING SERVICES"
        
        # Set file permissions
        if [[ -d "$PROJECT_DIR" ]]; then
            chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
        fi
        
        print_status "Starting emergency-app service..."
        systemctl start emergency-app
        
        print_status "Starting Nginx..."
        systemctl start nginx
        
        print_status "Checking service status..."
        systemctl is-active emergency-app nginx
        
        print_success "Services started successfully!"
    else
        print_header "STARTING APPLICATION (LOCAL MODE)"
        
        # Determine working directory
        if [[ -d "$PROJECT_DIR" ]] && check_root; then
            WORK_DIR="$PROJECT_DIR"
        else
            WORK_DIR="$(pwd)"
        fi
        
        cd "$WORK_DIR"
        
        if [[ -f "app.py" ]]; then
            print_status "Starting application in background..."
            source $VENV_NAME/bin/activate
            nohup python app.py > app.log 2>&1 &
            echo $! > app.pid
            print_success "Application started! PID: $(cat app.pid)"
            print_status "Logs: tail -f app.log"
        else
            print_warning "app.py not found. Please start the application manually."
        fi
    fi
}

# Start monitoring stack
start_monitoring() {
    print_header "STARTING MONITORING STACK"
    
    # Determine working directory
    if [[ -d "$PROJECT_DIR" ]] && check_root; then
        WORK_DIR="$PROJECT_DIR"
    else
        WORK_DIR="$(pwd)"
    fi
    
    cd "$WORK_DIR"
    
    if [[ -f "docker-compose.monitoring.yml" ]]; then
        print_status "Starting monitoring services..."
        docker-compose -f docker-compose.monitoring.yml up -d
        
        print_status "Waiting for services to start..."
        sleep 10
        
        print_status "Checking container status..."
        docker ps
        
        print_success "Monitoring stack started!"
    else
        print_warning "docker-compose.monitoring.yml not found. Skipping monitoring setup."
    fi
}

# Test deployment
test_deployment() {
    print_header "TESTING DEPLOYMENT"
    
    print_status "Testing application health..."
    if curl -s http://localhost:3000/api/v1/health > /dev/null; then
        print_success "Application is responding!"
    else
        print_warning "Application health check failed"
    fi
    
    print_status "Testing Prometheus..."
    if curl -s http://localhost:9090/-/healthy > /dev/null; then
        print_success "Prometheus is healthy!"
    else
        print_warning "Prometheus health check failed"
    fi
    
    print_status "Testing Grafana..."
    if curl -s http://localhost:3001/api/health > /dev/null; then
        print_success "Grafana is healthy!"
    else
        print_warning "Grafana health check failed"
    fi
}

# Print final information
print_final_info() {
    print_header "SETUP COMPLETED!"
    
    echo -e "${GREEN}🎉 Emergency Response App Setup Complete!${NC}"
    echo ""
    echo -e "${CYAN}📱 Application URLs:${NC}"
    
    if check_root; then
        echo -e "   🌐 Main App: http://$VPS_HOST"
        echo -e "   🌐 Main App: http://$VPS_HOSTNAME"
        echo -e "   🔗 API Health: http://$VPS_HOST/api/v1/health"
        echo -e "   📈 Prometheus: http://$VPS_HOST:9090"
        echo -e "   📊 Grafana: http://$VPS_HOST:3001"
    else
        echo -e "   🌐 Main App: http://localhost:3000"
        echo -e "   🔗 API Health: http://localhost:3000/api/v1/health"
        echo -e "   📈 Prometheus: http://localhost:9090"
        echo -e "   📊 Grafana: http://localhost:3001"
    fi
    
    echo ""
    echo -e "${CYAN}🔑 Login Credentials:${NC}"
    echo -e "   👤 Regular User: testuser / password123"
    echo -e "   🚒 Fire Department: fireuser / password123"
    echo -e "   📊 Grafana: admin / emergency123"
    
    echo ""
    echo -e "${CYAN}🔧 Management Commands:${NC}"
    if check_root; then
        echo -e "   📊 Check Status: systemctl status emergency-app nginx"
        echo -e "   📝 View Logs: journalctl -u emergency-app -f"
        echo -e "   🔄 Restart: systemctl restart emergency-app"
    else
        echo -e "   📊 Check Process: ps aux | grep python"
        echo -e "   📝 View Logs: tail -f app.log"
        echo -e "   🛑 Stop: kill \$(cat app.pid)"
    fi
    
    echo ""
    echo -e "${GREEN}🚑 Your Emergency Response App is ready to help save lives!${NC}"
}

# Main setup function
main() {
    print_header "EMERGENCY RESPONSE APP SETUP"
    echo -e "${BLUE}Starting automated setup for $PROJECT_NAME${NC}"
    echo ""
    
    # Parse command line arguments
    INSTALL_DOCKER=false
    START_MONITORING=false
    PRODUCTION_MODE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker)
                INSTALL_DOCKER=true
                shift
                ;;
            --monitoring)
                START_MONITORING=true
                shift
                ;;
            --production)
                PRODUCTION_MODE=true
                INSTALL_DOCKER=true
                START_MONITORING=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --docker      Install Docker and Docker Compose"
                echo "  --monitoring  Start monitoring stack (Prometheus/Grafana)"
                echo "  --production  Full production setup (includes Docker and monitoring)"
                echo "  --help        Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                    # Basic local development setup"
                echo "  $0 --docker          # Setup with Docker"
                echo "  $0 --production       # Full production deployment"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Detect OS
    detect_os
    
    # Check if we have required files
    if [[ ! -f "app.py" ]]; then
        print_error "app.py not found! Please run this script from the project directory."
        exit 1
    fi
    
    # Run setup steps
    install_system_deps
    
    if check_root && [[ "$PRODUCTION_MODE" == true ]]; then
        create_app_user
    fi
    
    setup_python_env
    init_database
    
    if check_root && [[ "$PRODUCTION_MODE" == true ]]; then
        setup_systemd_service
        configure_nginx
        configure_firewall
    fi
    
    if [[ "$INSTALL_DOCKER" == true ]]; then
        install_docker
    fi
    
    start_services
    
    if [[ "$START_MONITORING" == true ]] && [[ "$INSTALL_DOCKER" == true ]]; then
        start_monitoring
    fi
    
    # Wait a moment for services to start
    sleep 5
    
    test_deployment
    print_final_info
}

# Run main function with all arguments
main "$@"
