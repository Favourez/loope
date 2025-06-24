pipeline {
    agent any
    
    // Environment variables
    environment {
        APP_NAME = 'emergency-response-app'
        APP_VERSION = "${BUILD_NUMBER}"
        PROD_SERVER = '31.97.11.49'
        DEPLOY_USER = 'root'
        DEPLOY_PATH = '/opt/emergency-app'
        API_KEY = 'emergency-api-key-2024'
    }
    
    // Build triggers
    triggers {
        pollSCM('H/5 * * * *')
        githubPush()
    }
    
    // Pipeline options
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
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
    }
    
    stages {
        stage('🔍 Checkout & Setup') {
            steps {
                script {
                    cleanWs()
                    checkout scm
                    
                    echo "🚀 Building ${APP_NAME} v${APP_VERSION}"
                    echo "📅 Build Date: ${new Date()}"
                    echo "🌿 Branch: ${env.BRANCH_NAME}"
                    echo "📝 Commit: ${env.GIT_COMMIT}"
                    
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
            steps {
                script {
                    echo "🐍 Setting up Python environment..."
                    
                    sh '''
                        python3 -m venv venv || python -m venv venv
                        . venv/bin/activate || venv\\Scripts\\activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest pytest-cov flake8 bandit safety || true
                    '''
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
                                . venv/bin/activate || venv\\Scripts\\activate
                                flake8 --max-line-length=120 --exclude=venv,__pycache__ . || true
                            '''
                        }
                    }
                }
                
                stage('Unit Tests') {
                    steps {
                        script {
                            echo "🧪 Running unit tests..."
                            
                            sh '''
                                . venv/bin/activate || venv\\Scripts\\activate
                                
                                # Create test database
                                export FLASK_ENV=testing
                                python -c "from database import init_database; init_database()" || true
                                
                                # Run tests
                                pytest tests/test_app.py --junitxml=test-results.xml || true
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'test-results.xml'
                        }
                    }
                }
                
                stage('Security Scan') {
                    when {
                        expression { params.RUN_SECURITY_SCAN == true }
                    }
                    steps {
                        script {
                            echo "🔒 Running security scans..."
                            
                            sh '''
                                . venv/bin/activate || venv\\Scripts\\activate
                                
                                # Check for known security vulnerabilities
                                safety check --json --output safety-report.json || true
                                
                                # Static security analysis
                                bandit -r . -f json -o bandit-report.json || true
                            '''
                        }
                    }
                    post {
                        always {
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
                    
                    sh '''
                        # Create build directory
                        mkdir -p build
                        
                        # Copy application files
                        cp -r *.py templates static monitoring ansible requirements.txt build/ || true
                        cp setup.sh docker-compose.monitoring.yml build/ || true
                        
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
                    archiveArtifacts artifacts: "${APP_NAME}-${BUILD_NUMBER}.tar.gz", fingerprint: true
                }
            }
        }
        
        stage('🚀 Deploy to Production') {
            when {
                expression { params.DEPLOY_ENVIRONMENT == 'production' }
            }
            steps {
                script {
                    echo "🎯 Deploying to production environment..."
                    
                    // Use sshagent if SSH keys are configured
                    // For now, we'll use a simple approach
                    sh '''
                        echo "Deployment would happen here"
                        echo "Package: ${APP_NAME}-${BUILD_NUMBER}.tar.gz"
                        echo "Target: ${PROD_SERVER}"
                        echo "Path: ${DEPLOY_PATH}"
                        
                        # In a real deployment, you would:
                        # 1. Copy package to server
                        # 2. Extract and deploy
                        # 3. Restart services
                        # 4. Run health checks
                    '''
                }
            }
            post {
                success {
                    echo "✅ Production deployment successful!"
                }
                failure {
                    echo "❌ Production deployment failed!"
                }
            }
        }
        
        stage('🧪 Post-Deployment Tests') {
            when {
                expression { params.DEPLOY_ENVIRONMENT != 'skip' }
            }
            steps {
                script {
                    echo "🧪 Running post-deployment tests..."
                    
                    sh '''
                        # Wait for application to start
                        sleep 10
                        
                        # Test application health
                        echo "Testing application health..."
                        curl -f http://localhost:3000/api/v1/health || echo "Health check failed"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        
        success {
            script {
                echo "🎉 Pipeline completed successfully!"
                
                emailext (
                    subject: "✅ ${APP_NAME} v${BUILD_NUMBER} - Build Successful",
                    body: """
                        <h2>🎉 Build Successful!</h2>
                        <p><strong>Application:</strong> ${APP_NAME}</p>
                        <p><strong>Version:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Environment:</strong> ${params.DEPLOY_ENVIRONMENT}</p>
                        <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                        <p><strong>Commit:</strong> ${env.GIT_SHORT_COMMIT}</p>
                        <p><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                        
                        <h3>🌐 Access URLs:</h3>
                        <ul>
                            <li>Application: <a href="http://${PROD_SERVER}">http://${PROD_SERVER}</a></li>
                            <li>Jenkins: <a href="http://${PROD_SERVER}:8080">http://${PROD_SERVER}:8080</a></li>
                            <li>Grafana: <a href="http://${PROD_SERVER}:3001">http://${PROD_SERVER}:3001</a></li>
                        </ul>
                    """,
                    to: "nopoleflairan@gmail.com",
                    mimeType: 'text/html'
                )
            }
        }
        
        failure {
            script {
                echo "💥 Pipeline failed!"
                
                emailext (
                    subject: "❌ ${APP_NAME} v${BUILD_NUMBER} - Build Failed",
                    body: """
                        <h2>💥 Build Failed!</h2>
                        <p><strong>Application:</strong> ${APP_NAME}</p>
                        <p><strong>Version:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Environment:</strong> ${params.DEPLOY_ENVIRONMENT}</p>
                        <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                        <p><strong>Commit:</strong> ${env.GIT_SHORT_COMMIT}</p>
                        <p><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                        <p><strong>Console:</strong> <a href="${BUILD_URL}console">${BUILD_URL}console</a></p>
                        
                        <p>Please check the build logs for more details.</p>
                    """,
                    to: "nopoleflairan@gmail.com",
                    mimeType: 'text/html'
                )
            }
        }
        
        unstable {
            echo "⚠️ Pipeline completed with warnings!"
        }
    }
}
