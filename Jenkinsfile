pipeline {
    agent any
    
    // Environment variables
    environment {
        // Application settings
        APP_NAME = 'emergency-response-app'
        APP_VERSION = "${BUILD_NUMBER}"
        PYTHON_VERSION = '3.12'
        
        // VPS deployment settings
        PROD_SERVER = '31.97.11.49'
        STAGING_SERVER = 'staging.srv878357.hstgr.cloud'
        DEPLOY_USER = 'root'
        DEPLOY_PATH = '/opt/emergency-app'
        
        // Docker settings
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = "${APP_NAME}:${BUILD_NUMBER}"
        
        // Notification settings
        SLACK_CHANNEL = '#emergency-app-deployments'
        EMAIL_RECIPIENTS = 'admin@emergency-app.com'
        
        // Security
        SONAR_PROJECT_KEY = 'emergency-response-app'
    }
    
    // Build triggers
    triggers {
        // Poll SCM every 5 minutes for changes
        pollSCM('H/5 * * * *')
        
        // Trigger builds on GitHub webhook
        githubPush()
    }
    
    // Pipeline options
    options {
        // Keep only last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        
        // Timeout after 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        
        // Disable concurrent builds
        disableConcurrentBuilds()
        
        // Add timestamps to console output
        timestamps()
    }
    
    // Pipeline parameters
    parameters {
        choice(
            name: 'DEPLOY_ENVIRONMENT',
            choices: ['staging', 'production', 'skip'],
            description: 'Select deployment environment'
        )
        booleanParam(
            name: 'RUN_SECURITY_SCAN',
            defaultValue: true,
            description: 'Run security vulnerability scan'
        )
        booleanParam(
            name: 'DEPLOY_MONITORING',
            defaultValue: true,
            description: 'Deploy monitoring stack (Prometheus/Grafana)'
        )
        string(
            name: 'CUSTOM_TAG',
            defaultValue: '',
            description: 'Custom Docker tag (optional)'
        )
    }
    
    stages {
        stage('🔍 Checkout & Setup') {
            steps {
                script {
                    // Clean workspace
                    cleanWs()
                    
                    // Checkout source code
                    checkout scm
                    
                    // Display build information
                    echo "🚀 Building ${APP_NAME} v${APP_VERSION}"
                    echo "📅 Build Date: ${new Date()}"
                    echo "🌿 Branch: ${env.BRANCH_NAME}"
                    echo "📝 Commit: ${env.GIT_COMMIT}"
                    
                    // Set dynamic environment variables
                    env.BUILD_TIMESTAMP = sh(
                        script: "date +%Y%m%d-%H%M%S",
                        returnStdout: true
                    ).trim()
                    
                    env.GIT_SHORT_COMMIT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('🔧 Environment Setup') {
            parallel {
                stage('Python Environment') {
                    steps {
                        script {
                            echo "🐍 Setting up Python environment..."
                            
                            // Create virtual environment
                            sh '''
                                python3 -m venv venv
                                source venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install pytest pytest-cov flake8 bandit safety
                            '''
                        }
                    }
                }
                
                stage('Docker Environment') {
                    when {
                        anyOf {
                            params.DEPLOY_ENVIRONMENT == 'staging'
                            params.DEPLOY_ENVIRONMENT == 'production'
                        }
                    }
                    steps {
                        script {
                            echo "🐳 Setting up Docker environment..."
                            
                            // Verify Docker is available
                            sh 'docker --version'
                            sh 'docker-compose --version'
                        }
                    }
                }
            }
        }
        
        stage('🧪 Code Quality & Testing') {
            parallel {
                stage('Linting') {
                    steps {
                        script {
                            echo "🔍 Running code linting..."
                            
                            sh '''
                                source venv/bin/activate
                                flake8 --max-line-length=120 --exclude=venv,__pycache__ .
                            '''
                        }
                    }
                    post {
                        always {
                            // Archive linting results
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: '.',
                                reportFiles: 'flake8-report.html',
                                reportName: 'Flake8 Report'
                            ])
                        }
                    }
                }
                
                stage('Unit Tests') {
                    steps {
                        script {
                            echo "🧪 Running unit tests..."
                            
                            sh '''
                                source venv/bin/activate
                                
                                # Create test database
                                export FLASK_ENV=testing
                                python -c "from database import init_database; init_database()"
                                
                                # Run tests with coverage
                                pytest --cov=. --cov-report=xml --cov-report=html --junitxml=test-results.xml
                            '''
                        }
                    }
                    post {
                        always {
                            // Publish test results
                            junit 'test-results.xml'
                            
                            // Publish coverage report
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'htmlcov',
                                reportFiles: 'index.html',
                                reportName: 'Coverage Report'
                            ])
                        }
                    }
                }
                
                stage('Security Scan') {
                    when {
                        params.RUN_SECURITY_SCAN == true
                    }
                    steps {
                        script {
                            echo "🔒 Running security scans..."
                            
                            sh '''
                                source venv/bin/activate
                                
                                # Check for known security vulnerabilities
                                safety check --json --output safety-report.json || true
                                
                                # Static security analysis
                                bandit -r . -f json -o bandit-report.json || true
                            '''
                        }
                    }
                    post {
                        always {
                            // Archive security reports
                            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        stage('🏗️ Build Application') {
            steps {
                script {
                    echo "🏗️ Building application..."
                    
                    // Create application package
                    sh '''
                        # Create build directory
                        mkdir -p build
                        
                        # Copy application files
                        cp -r *.py templates static monitoring ansible requirements.txt build/
                        cp setup.sh docker-compose.monitoring.yml build/
                        
                        # Create version file
                        echo "${BUILD_NUMBER}" > build/VERSION
                        echo "${GIT_SHORT_COMMIT}" > build/COMMIT
                        echo "${BUILD_TIMESTAMP}" > build/BUILD_DATE
                        
                        # Create deployment package
                        tar -czf ${APP_NAME}-${BUILD_NUMBER}.tar.gz -C build .
                    '''
                }
            }
            post {
                always {
                    // Archive build artifacts
                    archiveArtifacts artifacts: "${APP_NAME}-${BUILD_NUMBER}.tar.gz", fingerprint: true
                }
            }
        }
        
        stage('🐳 Docker Build') {
            when {
                anyOf {
                    params.DEPLOY_ENVIRONMENT == 'staging'
                    params.DEPLOY_ENVIRONMENT == 'production'
                }
            }
            steps {
                script {
                    echo "🐳 Building Docker image..."
                    
                    // Create Dockerfile if it doesn't exist
                    writeFile file: 'Dockerfile', text: '''
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -r -s /bin/bash emergency
RUN chown -R emergency:emergency /app
USER emergency

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:3000/api/v1/health || exit 1

# Start application
CMD ["python", "app.py"]
'''
                    
                    // Build Docker image
                    def dockerTag = params.CUSTOM_TAG ?: "${BUILD_NUMBER}"
                    def dockerImage = docker.build("${APP_NAME}:${dockerTag}")
                    
                    // Tag for registry
                    dockerImage.tag("${APP_NAME}:latest")
                    dockerImage.tag("${APP_NAME}:${env.BRANCH_NAME}-${BUILD_NUMBER}")
                    
                    // Store image reference
                    env.DOCKER_IMAGE_ID = dockerImage.id
                }
            }
        }
        
        stage('🚀 Deploy to Staging') {
            when {
                anyOf {
                    params.DEPLOY_ENVIRONMENT == 'staging'
                    branch 'develop'
                }
            }
            steps {
                script {
                    echo "🚀 Deploying to staging environment..."
                    
                    // Deploy to staging server
                    sshagent(['staging-server-key']) {
                        sh '''
                            # Copy deployment package
                            scp ${APP_NAME}-${BUILD_NUMBER}.tar.gz ${DEPLOY_USER}@${STAGING_SERVER}:/tmp/
                            
                            # Deploy on staging server
                            ssh ${DEPLOY_USER}@${STAGING_SERVER} "
                                cd /opt/emergency-app-staging
                                
                                # Backup current version
                                if [ -d 'current' ]; then
                                    mv current backup-$(date +%Y%m%d-%H%M%S)
                                fi
                                
                                # Extract new version
                                mkdir current
                                cd current
                                tar -xzf /tmp/${APP_NAME}-${BUILD_NUMBER}.tar.gz
                                
                                # Run setup script
                                chmod +x setup.sh
                                ./setup.sh --production
                                
                                # Start services
                                systemctl restart emergency-app-staging
                            "
                        '''
                    }
                }
            }
            post {
                success {
                    echo "✅ Staging deployment successful!"
                }
                failure {
                    echo "❌ Staging deployment failed!"
                }
            }
        }
        
        stage('🧪 Integration Tests') {
            when {
                anyOf {
                    params.DEPLOY_ENVIRONMENT == 'staging'
                    params.DEPLOY_ENVIRONMENT == 'production'
                }
            }
            steps {
                script {
                    echo "🧪 Running integration tests..."
                    
                    sh '''
                        source venv/bin/activate
                        
                        # Wait for application to start
                        sleep 30
                        
                        # Run API tests against staging
                        python -m pytest tests/integration/ --staging-url=http://${STAGING_SERVER}
                    '''
                }
            }
        }
        
        stage('🎯 Deploy to Production') {
            when {
                allOf {
                    params.DEPLOY_ENVIRONMENT == 'production'
                    anyOf {
                        branch 'main'
                        branch 'master'
                    }
                }
            }
            steps {
                script {
                    // Manual approval for production deployment
                    timeout(time: 10, unit: 'MINUTES') {
                        input message: 'Deploy to Production?', 
                              ok: 'Deploy',
                              submitterParameter: 'APPROVER'
                    }
                    
                    echo "🎯 Deploying to production environment..."
                    echo "👤 Approved by: ${env.APPROVER}"
                    
                    // Deploy to production server
                    sshagent(['production-server-key']) {
                        sh '''
                            # Copy deployment package
                            scp ${APP_NAME}-${BUILD_NUMBER}.tar.gz ${DEPLOY_USER}@${PROD_SERVER}:/tmp/
                            
                            # Deploy on production server
                            ssh ${DEPLOY_USER}@${PROD_SERVER} "
                                cd ${DEPLOY_PATH}
                                
                                # Backup current version
                                if [ -d 'current' ]; then
                                    mv current backup-$(date +%Y%m%d-%H%M%S)
                                fi
                                
                                # Extract new version
                                mkdir current
                                cd current
                                tar -xzf /tmp/${APP_NAME}-${BUILD_NUMBER}.tar.gz
                                
                                # Run setup script
                                chmod +x setup.sh
                                ./setup.sh --production
                                
                                # Deploy monitoring if requested
                                if [ '${params.DEPLOY_MONITORING}' = 'true' ]; then
                                    docker-compose -f docker-compose.monitoring.yml up -d
                                fi
                                
                                # Restart services
                                systemctl restart emergency-app nginx
                                
                                # Health check
                                sleep 30
                                curl -f http://localhost:3000/api/v1/health
                            "
                        '''
                    }
                }
            }
            post {
                success {
                    echo "✅ Production deployment successful!"
                }
                failure {
                    echo "❌ Production deployment failed!"
                    
                    // Rollback on failure
                    sshagent(['production-server-key']) {
                        sh '''
                            ssh ${DEPLOY_USER}@${PROD_SERVER} "
                                cd ${DEPLOY_PATH}
                                
                                # Find latest backup
                                BACKUP_DIR=$(ls -1t backup-* | head -1)
                                
                                if [ -n '$BACKUP_DIR' ]; then
                                    echo 'Rolling back to: $BACKUP_DIR'
                                    rm -rf current
                                    mv $BACKUP_DIR current
                                    systemctl restart emergency-app nginx
                                fi
                            "
                        '''
                    }
                }
            }
        }
        
        stage('📊 Post-Deployment Verification') {
            when {
                anyOf {
                    params.DEPLOY_ENVIRONMENT == 'staging'
                    params.DEPLOY_ENVIRONMENT == 'production'
                }
            }
            parallel {
                stage('Health Checks') {
                    steps {
                        script {
                            echo "🏥 Running health checks..."
                            
                            def targetServer = params.DEPLOY_ENVIRONMENT == 'production' ? PROD_SERVER : STAGING_SERVER
                            
                            sh """
                                # Wait for services to stabilize
                                sleep 60
                                
                                # Check application health
                                curl -f http://${targetServer}/api/v1/health
                                
                                # Check monitoring services
                                curl -f http://${targetServer}:9090/-/healthy
                                curl -f http://${targetServer}:3001/api/health
                            """
                        }
                    }
                }
                
                stage('Performance Tests') {
                    steps {
                        script {
                            echo "⚡ Running performance tests..."
                            
                            sh '''
                                # Install Apache Bench if not available
                                which ab || apt-get update && apt-get install -y apache2-utils
                                
                                # Run basic load test
                                ab -n 100 -c 10 http://${PROD_SERVER}/api/v1/health
                            '''
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean up workspace
            cleanWs()
        }
        
        success {
            script {
                echo "🎉 Pipeline completed successfully!"
                
                // Send success notification
                emailext (
                    subject: "✅ ${APP_NAME} v${BUILD_NUMBER} - Deployment Successful",
                    body: """
                        <h2>🎉 Deployment Successful!</h2>
                        <p><strong>Application:</strong> ${APP_NAME}</p>
                        <p><strong>Version:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Environment:</strong> ${params.DEPLOY_ENVIRONMENT}</p>
                        <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                        <p><strong>Commit:</strong> ${env.GIT_SHORT_COMMIT}</p>
                        <p><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                        
                        <h3>🌐 Access URLs:</h3>
                        <ul>
                            <li>Application: <a href="http://${PROD_SERVER}">http://${PROD_SERVER}</a></li>
                            <li>Grafana: <a href="http://${PROD_SERVER}:3001">http://${PROD_SERVER}:3001</a></li>
                            <li>Prometheus: <a href="http://${PROD_SERVER}:9090">http://${PROD_SERVER}:9090</a></li>
                        </ul>
                    """,
                    to: "${EMAIL_RECIPIENTS}",
                    mimeType: 'text/html'
                )
            }
        }
        
        failure {
            script {
                echo "💥 Pipeline failed!"
                
                // Send failure notification
                emailext (
                    subject: "❌ ${APP_NAME} v${BUILD_NUMBER} - Deployment Failed",
                    body: """
                        <h2>💥 Deployment Failed!</h2>
                        <p><strong>Application:</strong> ${APP_NAME}</p>
                        <p><strong>Version:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Environment:</strong> ${params.DEPLOY_ENVIRONMENT}</p>
                        <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                        <p><strong>Commit:</strong> ${env.GIT_SHORT_COMMIT}</p>
                        <p><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                        <p><strong>Console:</strong> <a href="${BUILD_URL}console">${BUILD_URL}console</a></p>
                        
                        <p>Please check the build logs for more details.</p>
                    """,
                    to: "${EMAIL_RECIPIENTS}",
                    mimeType: 'text/html'
                )
            }
        }
        
        unstable {
            echo "⚠️ Pipeline completed with warnings!"
        }
    }
}
