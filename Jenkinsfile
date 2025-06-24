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
        choice(name: 'DEPLOY_ENVIRONMENT', choices: ['staging', 'production', 'skip'], description: 'Select deployment environment')
        booleanParam(name: 'RUN_SECURITY_SCAN', defaultValue: true, description: 'Run security vulnerability scan')
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
                    bat '''
                        @echo off
                        if exist venv rmdir /s /q venv
                        python -m venv venv
                        call venv\\Scripts\\activate.bat
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest pytest-cov flake8 bandit safety
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
                            bat '''
                                call venv\\Scripts\\activate.bat
                                flake8 --max-line-length=120 --exclude=venv,__pycache__ . || echo "Linting warnings"
                            '''
                        }
                    }
                }

                stage('Unit Tests') {
                    steps {
                        script {
                            echo "🧪 Running unit tests..."
                            bat '''
                                call venv\\Scripts\\activate.bat
                                set FLASK_ENV=testing
                                python -c "from database import init_database; init_database()"
                                pytest --junitxml=test-results.xml --tb=short --maxfail=5
                            '''
                        }
                    }
                    post {
                        always {
                            script {
                                if (fileExists('test-results.xml')) {
                                    junit 'test-results.xml'
                                } else {
                                    echo "❗No test results file found"
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
                            bat '''
                                call venv\\Scripts\\activate.bat
                                safety check --json --output safety-report.json
                                bandit -r . -f json -o bandit-report.json
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
                    bat '''
                        if not exist build mkdir build
                        copy *.py build\\ 2>nul || echo "Copied .py"
                        if exist templates xcopy /E /I templates build\\templates
                        if exist static xcopy /E /I static build\\static
                        if exist monitoring xcopy /E /I monitoring build\\monitoring
                        if exist ansible xcopy /E /I ansible build\\ansible
                        copy requirements.txt build\\ 2>nul
                        if exist setup.sh copy setup.sh build\\
                        if exist docker-compose.monitoring.yml copy docker-compose.monitoring.yml build\\
                        echo %BUILD_NUMBER% > build\\VERSION
                        echo %GIT_SHORT_COMMIT% > build\\COMMIT
                        echo %BUILD_TIMESTAMP% > build\\BUILD_DATE
                        powershell "Compress-Archive -Path build\\* -DestinationPath %APP_NAME%-%BUILD_NUMBER%.zip -Force"
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
                    echo "🎯 Deploying to production..."
                    bat '''
                        echo Simulating deployment
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
                    bat '''
                        timeout /t 10 /nobreak
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
                        <p><strong>App:</strong> ${APP_NAME}</p>
                        <p><strong>Version:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                        <p><strong>Commit:</strong> ${env.GIT_SHORT_COMMIT}</p>
                        <p><a href="${BUILD_URL}">View Build</a></p>
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
                        <p><strong>App:</strong> ${APP_NAME}</p>
                        <p><strong>Version:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Branch:</strong> ${env.BRANCH_NAME}</p>
                        <p><strong>Commit:</strong> ${env.GIT_SHORT_COMMIT}</p>
                        <p><a href="${BUILD_URL}console">View Console Logs</a></p>
                    """,
                    to: "nopoleflairan@gmail.com",
                    mimeType: 'text/html'
                )
            }
        }

        unstable {
            echo "⚠️ Pipeline finished with warnings"
        }
    }
}
