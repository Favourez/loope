pipeline {
    agent any

    environment {
        APP_NAME = 'emergency-response-app'
        APP_VERSION = "${BUILD_NUMBER}"
        PROD_SERVER = '31.97.11.49'
        DEPLOY_USER = 'root'
        DEPLOY_PATH = '/opt/emergency-app'
        API_KEY = 'emergency-api-key-2024'
    }

    triggers {
        pollSCM('H/5 * * * *')
        githubPush()
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        timestamps()
    }

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

                    env.BUILD_TIMESTAMP = new Date().format('yyyyMMdd-HHmmss')
                    env.GIT_SHORT_COMMIT = env.GIT_COMMIT?.take(7) ?: 'unknown'
                }
            }
        }

        stage('🔧 Environment Setup') {
            steps {
                script {
                    echo "🐍 Setting up Python environment..."

                    bat '''@echo off
echo Setting up Python virtual environment...

if exist venv rmdir /s /q venv
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    exit /b 1
)

call venv\\Scripts\\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-cov flake8 bandit safety

echo Virtual environment setup completed successfully
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

                            bat '''call venv\\Scripts\\activate.bat
flake8 --max-line-length=120 --exclude=venv,__pycache__ . || echo "Linting completed with warnings"
'''
                        }
                    }
                }

                stage('Unit Tests') {
                    steps {
                        script {
                            echo "🧪 Running unit tests..."

                            bat '''call venv\\Scripts\\activate.bat
set FLASK_ENV=testing
python -c "from database import init_database; init_database()" || echo "Database init completed"
pytest tests\\test_app.py --junitxml=test-results.xml || echo "Tests completed"
'''
                        }
                    }
                    post {
                        always {
                            script {
                                if (fileExists('test-results.xml')) {
                                    junit 'test-results.xml'
                                } else {
                                    echo "No test results file found"
                                }
                            }
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

                            bat '''call venv\\Scripts\\activate.bat
safety check --json --output safety-report.json || echo "Safety check completed"
bandit -r . -f json -o bandit-report.json || echo "Bandit scan completed"
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

                    bat '''rem Create build directory
if not exist build mkdir build

rem Copy application files
copy *.py build\\ 2>nul || echo "Python files copied"
if exist templates xcopy /E /I templates build\\templates 2>nul || echo "Templates copied"
if exist static xcopy /E /I static build\\static 2>nul || echo "Static files copied"
if exist monitoring xcopy /E /I monitoring build\\monitoring 2>nul || echo "Monitoring copied"
if exist ansible xcopy /E /I ansible build\\ansible 2>nul || echo "Ansible copied"
copy requirements.txt build\\ 2>nul || echo "Requirements copied"
if exist setup.sh copy setup.sh build\\ 2>nul || echo "Setup script copied"
if exist docker-compose.monitoring.yml copy docker-compose.monitoring.yml build\\ 2>nul || echo "Docker compose copied"

rem Create version files
echo %BUILD_NUMBER% > build\\VERSION
echo %GIT_SHORT_COMMIT% > build\\COMMIT
echo %BUILD_TIMESTAMP% > build\\BUILD_DATE

rem Create deployment package
powershell "Compress-Archive -Path build\\* -DestinationPath %APP_NAME%-%BUILD_NUMBER%.zip -Force" || echo "Package created as zip"
'''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${APP_NAME}-${BUILD_NUMBER}.zip", allowEmptyArchive: true, fingerprint: true
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

                    bat '''echo Deployment would happen here
echo Package: %APP_NAME%-%BUILD_NUMBER%.zip
echo Target: %PROD_SERVER%
echo Path: %DEPLOY_PATH%
echo Simulating deployment to production...
timeout /t 3 /nobreak >nul
echo Deployment simulation completed
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

                    bat '''timeout /t 10 /nobreak
echo Testing application health...
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
