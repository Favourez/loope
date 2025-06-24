# 🚀 CI/CD Setup Guide - Emergency Response App

## 📋 Overview

This guide provides complete setup instructions for implementing CI/CD pipeline using Jenkins for the Emergency Response App, including GitHub/GitLab integration, automated testing, and deployment.

## 🏗️ Pipeline Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   GitHub/   │───▶│   Jenkins    │───▶│   Staging   │───▶│ Production   │
│   GitLab    │    │   Pipeline   │    │ Environment │    │ Environment  │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
       │                   │                   │                   │
       │                   ▼                   ▼                   ▼
   Code Push         ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
   Webhook          │ Build & Test │    │ Integration │    │ Health Check │
                    │   - Lint     │    │    Tests    │    │ & Monitoring │
                    │   - Unit     │    │             │    │              │
                    │   - Security │    │             │    │              │
                    └──────────────┘    └─────────────┘    └──────────────┘
```

## 🔧 Jenkins Setup

### 1. Jenkins Installation

#### Option A: Docker Installation (Recommended)
```bash
# Create Jenkins directory
mkdir -p /opt/jenkins
cd /opt/jenkins

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JAVA_OPTS=-Djenkins.install.runSetupWizard=false
    restart: unless-stopped

volumes:
  jenkins_home:
EOF

# Start Jenkins
docker-compose up -d

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

#### Option B: Native Installation (Ubuntu)
```bash
# Add Jenkins repository
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

# Install Jenkins
sudo apt update
sudo apt install jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### 2. Jenkins Initial Configuration

1. **Access Jenkins**: http://your-server:8080
2. **Install suggested plugins**
3. **Create admin user**
4. **Install additional plugins**:
   - GitHub Integration Plugin
   - GitLab Plugin
   - Docker Pipeline Plugin
   - Email Extension Plugin
   - HTML Publisher Plugin
   - SSH Agent Plugin
   - Prometheus Plugin

### 3. Required Jenkins Plugins

```bash
# Install via Jenkins CLI (optional)
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin \
  github \
  gitlab-plugin \
  docker-workflow \
  email-ext \
  htmlpublisher \
  ssh-agent \
  prometheus \
  pipeline-stage-view \
  build-timeout \
  timestamper
```

## 🔐 Credentials Setup

### 1. SSH Keys for Deployment
```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "jenkins@emergency-app" -f ~/.ssh/jenkins_deploy_key

# Add public key to target servers
ssh-copy-id -i ~/.ssh/jenkins_deploy_key.pub root@31.97.11.49
ssh-copy-id -i ~/.ssh/jenkins_deploy_key.pub root@staging.srv878357.hstgr.cloud
```

### 2. Jenkins Credentials Configuration

In Jenkins Dashboard → Manage Jenkins → Manage Credentials:

#### SSH Credentials
- **ID**: `production-server-key`
- **Type**: SSH Username with private key
- **Username**: `root`
- **Private Key**: Contents of `~/.ssh/jenkins_deploy_key`

#### GitHub/GitLab Credentials
- **ID**: `github-token` or `gitlab-token`
- **Type**: Secret text
- **Secret**: Your GitHub/GitLab personal access token

#### Email Credentials
- **ID**: `email-credentials`
- **Type**: Username with password
- **Username**: Your SMTP username
- **Password**: Your SMTP password

## 🔗 Source Control Integration

### GitHub Integration

#### 1. Repository Setup
```bash
# Add Jenkinsfile to your repository
git add Jenkinsfile CI_CD_SETUP.md
git commit -m "Add Jenkins CI/CD pipeline"
git push origin main
```

#### 2. Webhook Configuration
1. Go to GitHub repository → Settings → Webhooks
2. Add webhook:
   - **URL**: `http://your-jenkins-server:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Events**: Push events, Pull requests

#### 3. Jenkins Job Configuration
```groovy
// In Jenkins → New Item → Pipeline
pipeline {
    agent any
    triggers {
        githubPush()
    }
    // ... rest of pipeline
}
```

### GitLab Integration

#### 1. GitLab CI/CD Variables
In GitLab project → Settings → CI/CD → Variables:
- `JENKINS_URL`: Your Jenkins server URL
- `JENKINS_TOKEN`: Jenkins API token

#### 2. Webhook Configuration
1. Go to GitLab project → Settings → Webhooks
2. Add webhook:
   - **URL**: `http://your-jenkins-server:8080/project/your-job-name`
   - **Trigger**: Push events, Merge request events

## 🧪 Testing Configuration

### 1. Create Test Files

#### Unit Tests (`tests/test_app.py`)
```python
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import init_database

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_database()
        yield client

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert b'healthy' in response.data

def test_emergency_creation(client):
    """Test emergency report creation"""
    data = {
        'emergency_type': 'fire',
        'location': 'Test Location',
        'description': 'Test emergency',
        'severity': 'medium'
    }
    response = client.post('/api/v1/emergencies', 
                          json=data,
                          headers={'X-API-Key': 'emergency-api-key-2024'})
    assert response.status_code == 201

def test_first_aid_endpoint(client):
    """Test first aid practices endpoint"""
    response = client.get('/api/v1/first-aid')
    assert response.status_code == 200
```

#### Integration Tests (`tests/integration/test_api.py`)
```python
import requests
import pytest
import os

STAGING_URL = os.getenv('STAGING_URL', 'http://localhost:3000')
API_KEY = 'emergency-api-key-2024'

def test_staging_health():
    """Test staging environment health"""
    response = requests.get(f'{STAGING_URL}/api/v1/health')
    assert response.status_code == 200
    assert 'healthy' in response.json()['data']['status']

def test_staging_api_endpoints():
    """Test critical API endpoints on staging"""
    headers = {'X-API-Key': API_KEY}
    
    endpoints = [
        '/api/v1/status',
        '/api/v1/emergencies',
        '/api/v1/first-aid',
        '/api/v1/fire-departments'
    ]
    
    for endpoint in endpoints:
        response = requests.get(f'{STAGING_URL}{endpoint}', headers=headers)
        assert response.status_code == 200
```

### 2. Test Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=.
    --cov-report=html
    --cov-report=xml
    --junitxml=test-results.xml
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

## 📊 Monitoring & Notifications

### 1. Email Configuration

In Jenkins → Manage Jenkins → Configure System → Extended E-mail Notification:
```
SMTP Server: smtp.gmail.com
SMTP Port: 587
Use SMTP Authentication: ✓
Username: your-email@gmail.com
Password: your-app-password
Use SSL: ✓
```

### 2. Slack Integration (Optional)

#### Install Slack Plugin
```bash
# Install Slack Notification Plugin
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin slack
```

#### Configure Slack
1. Create Slack app and get webhook URL
2. In Jenkins → Configure System → Slack:
   - **Workspace**: Your workspace name
   - **Credential**: Add Slack token
   - **Channel**: `#emergency-app-deployments`

### 3. Prometheus Monitoring

#### Jenkins Metrics (`prometheus.yml`)
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'jenkins'
    static_configs:
      - targets: ['jenkins:8080']
    metrics_path: '/prometheus'
    
  - job_name: 'emergency-app'
    static_configs:
      - targets: ['31.97.11.49:3000']
    metrics_path: '/metrics'
```

## 🚀 Deployment Strategies

### 1. Blue-Green Deployment

```groovy
stage('Blue-Green Deployment') {
    steps {
        script {
            // Deploy to green environment
            sh '''
                ssh ${DEPLOY_USER}@${PROD_SERVER} "
                    # Stop green environment
                    systemctl stop emergency-app-green || true
                    
                    # Deploy new version to green
                    cd /opt/emergency-app-green
                    tar -xzf /tmp/${APP_NAME}-${BUILD_NUMBER}.tar.gz
                    ./setup.sh --production
                    
                    # Start green environment
                    systemctl start emergency-app-green
                    
                    # Health check green
                    sleep 30
                    curl -f http://localhost:3001/api/v1/health
                    
                    # Switch traffic to green
                    nginx -s reload
                "
            '''
        }
    }
}
```

### 2. Rolling Deployment

```groovy
stage('Rolling Deployment') {
    steps {
        script {
            def servers = ['server1', 'server2', 'server3']
            
            servers.each { server ->
                sh """
                    ssh ${DEPLOY_USER}@${server} "
                        systemctl stop emergency-app
                        cd /opt/emergency-app
                        tar -xzf /tmp/${APP_NAME}-${BUILD_NUMBER}.tar.gz
                        ./setup.sh --production
                        systemctl start emergency-app
                        sleep 30
                        curl -f http://localhost:3000/api/v1/health
                    "
                """
                
                // Wait between deployments
                sleep(30)
            }
        }
    }
}
```

## 🔧 Pipeline Customization

### 1. Environment-Specific Configuration

#### Development Pipeline (`Jenkinsfile.dev`)
```groovy
pipeline {
    agent any
    stages {
        stage('Quick Tests') {
            steps {
                sh 'pytest tests/unit/ -x'
            }
        }
        stage('Deploy to Dev') {
            steps {
                sh './setup.sh'
            }
        }
    }
}
```

#### Production Pipeline (`Jenkinsfile.prod`)
```groovy
pipeline {
    agent any
    stages {
        stage('Full Test Suite') {
            parallel {
                stage('Unit Tests') { /* ... */ }
                stage('Integration Tests') { /* ... */ }
                stage('Security Scan') { /* ... */ }
                stage('Performance Tests') { /* ... */ }
            }
        }
        stage('Manual Approval') {
            input message: 'Deploy to Production?'
        }
        stage('Production Deployment') {
            /* ... */
        }
    }
}
```

### 2. Multi-Branch Pipeline

```groovy
// Jenkinsfile for multi-branch pipeline
pipeline {
    agent any
    
    stages {
        stage('Branch-specific Logic') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        echo 'Production deployment'
                        // Production logic
                    } else if (env.BRANCH_NAME == 'develop') {
                        echo 'Staging deployment'
                        // Staging logic
                    } else {
                        echo 'Feature branch - run tests only'
                        // Test-only logic
                    }
                }
            }
        }
    }
}
```

## 📈 Performance Optimization

### 1. Pipeline Caching

```groovy
stage('Cache Dependencies') {
    steps {
        cache(maxCacheSize: 250, caches: [
            arbitraryFileCache(
                path: 'venv',
                includes: '**/*',
                fingerprinting: true
            )
        ]) {
            sh 'pip install -r requirements.txt'
        }
    }
}
```

### 2. Parallel Execution

```groovy
stage('Parallel Tests') {
    parallel {
        stage('Unit Tests') {
            agent { label 'test-runner-1' }
            steps { sh 'pytest tests/unit/' }
        }
        stage('Integration Tests') {
            agent { label 'test-runner-2' }
            steps { sh 'pytest tests/integration/' }
        }
        stage('Security Scan') {
            agent { label 'security-scanner' }
            steps { sh 'bandit -r .' }
        }
    }
}
```

## 🎯 Best Practices

### 1. Pipeline as Code
- Store Jenkinsfile in version control
- Use declarative pipeline syntax
- Implement proper error handling

### 2. Security
- Use Jenkins credentials for sensitive data
- Implement approval gates for production
- Regular security scans and updates

### 3. Monitoring
- Set up build notifications
- Monitor pipeline performance
- Track deployment success rates

### 4. Testing
- Implement comprehensive test coverage
- Use staging environment for integration tests
- Automated rollback on failure

## 🚀 Getting Started

1. **Setup Jenkins** using Docker or native installation
2. **Configure credentials** for SSH and source control
3. **Create pipeline job** in Jenkins
4. **Add Jenkinsfile** to your repository
5. **Configure webhooks** for automatic triggers
6. **Test the pipeline** with a sample commit

Your CI/CD pipeline is now ready to automate the build, test, and deployment of your Emergency Response App! 🎉
