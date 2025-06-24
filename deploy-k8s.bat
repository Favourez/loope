@echo off
REM Emergency Response App - Kubernetes Deployment Script for Windows
REM Deploys the application using Kubernetes manifests or Helm charts

echo 🚀 DEPLOYING EMERGENCY RESPONSE APP TO KUBERNETES
echo ==================================================

REM Configuration
set NAMESPACE=emergency-response
set DEPLOYMENT_METHOD=%1
set ENVIRONMENT=%2

if "%DEPLOYMENT_METHOD%"=="" set DEPLOYMENT_METHOD=helm
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development

echo [INFO] Deployment method: %DEPLOYMENT_METHOD%
echo [INFO] Environment: %ENVIRONMENT%

REM Check if kubectl is available
kubectl version --client >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] kubectl is not installed or not in PATH
    exit /b 1
)

REM Check if cluster is accessible
kubectl cluster-info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Cannot connect to Kubernetes cluster
    exit /b 1
)

echo [SUCCESS] Connected to Kubernetes cluster

REM Deploy based on method
if "%DEPLOYMENT_METHOD%"=="helm" goto deploy_helm
if "%DEPLOYMENT_METHOD%"=="kubectl" goto deploy_kubectl
if "%DEPLOYMENT_METHOD%"=="cleanup" goto cleanup

echo [ERROR] Invalid deployment method. Use 'helm', 'kubectl', or 'cleanup'
exit /b 1

:deploy_kubectl
echo [INFO] Deploying with kubectl...

REM Create namespace
echo [INFO] Creating namespace: %NAMESPACE%
kubectl create namespace %NAMESPACE% --dry-run=client -o yaml | kubectl apply -f -

REM Apply manifests in order
echo [INFO] Applying Kubernetes manifests...

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/persistent-volumes.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/deployments.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

if %errorlevel% neq 0 (
    echo [ERROR] Failed to apply manifests
    exit /b 1
)

echo [SUCCESS] All manifests applied successfully
goto verify

:deploy_helm
echo [INFO] Deploying with Helm...

REM Check if Helm is available
helm version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Helm is not installed or not in PATH
    exit /b 1
)

REM Create namespace
echo [INFO] Creating namespace: %NAMESPACE%
kubectl create namespace %NAMESPACE% --dry-run=client -o yaml | kubectl apply -f -

REM Add required Helm repositories
echo [INFO] Adding Helm repositories...
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

REM Deploy with Helm
echo [INFO] Installing Emergency Response App with Helm...

set VALUES_FILE=helm/emergency-response/values.yaml
if "%ENVIRONMENT%"=="production" set VALUES_FILE=helm/emergency-response/values-production.yaml
if "%ENVIRONMENT%"=="staging" set VALUES_FILE=helm/emergency-response/values-staging.yaml

if not exist "%VALUES_FILE%" (
    echo [WARNING] Values file %VALUES_FILE% not found, using default values.yaml
    set VALUES_FILE=helm/emergency-response/values.yaml
)

helm upgrade --install emergency-response ./helm/emergency-response --namespace %NAMESPACE% --values %VALUES_FILE% --wait --timeout 10m

if %errorlevel% neq 0 (
    echo [ERROR] Helm deployment failed
    exit /b 1
)

echo [SUCCESS] Helm deployment completed successfully
goto verify

:verify
echo [INFO] Verifying deployment...

REM Wait for pods to be ready
echo [INFO] Waiting for pods to be ready...
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=emergency-response --namespace=%NAMESPACE% --timeout=300s

REM Check deployment status
echo [INFO] Checking deployment status...
kubectl get deployments -n %NAMESPACE%
kubectl get pods -n %NAMESPACE%
kubectl get services -n %NAMESPACE%

REM Check HPA
kubectl get hpa -n %NAMESPACE% >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] HPA status:
    kubectl get hpa -n %NAMESPACE%
)

REM Get service URLs
echo [INFO] Service URLs:

REM Try to get external IP or NodePort
for /f "tokens=*" %%i in ('kubectl get service emergency-response-nginx -n %NAMESPACE% -o jsonpath="{.status.loadBalancer.ingress[0].ip}" 2^>nul') do set EXTERNAL_IP=%%i

if "%EXTERNAL_IP%"=="" (
    for /f "tokens=*" %%i in ('kubectl get service emergency-response-nginx -n %NAMESPACE% -o jsonpath="{.spec.ports[0].nodePort}" 2^>nul') do set NODE_PORT=%%i
    if not "%NODE_PORT%"=="" (
        for /f "tokens=*" %%i in ('kubectl get nodes -o jsonpath="{.items[0].status.addresses[?(@.type==\"InternalIP\")].address}" 2^>nul') do set NODE_IP=%%i
        echo [SUCCESS] Application URL: http://!NODE_IP!:!NODE_PORT!
    ) else (
        echo [WARNING] No external access configured. Use port-forward to access the application:
        echo [WARNING] kubectl port-forward service/emergency-response-nginx 8080:80 -n %NAMESPACE%
    )
) else (
    echo [SUCCESS] Application URL: http://%EXTERNAL_IP%
)

echo [INFO] Monitoring URLs:
echo [INFO] - Grafana: kubectl port-forward service/emergency-response-grafana 3000:3000 -n %NAMESPACE%
echo [INFO] - Prometheus: kubectl port-forward service/emergency-response-prometheus 9090:9090 -n %NAMESPACE%

echo [SUCCESS] Deployment verification completed

REM Show recent logs
echo [INFO] Recent application logs:
kubectl logs -l app.kubernetes.io/name=emergency-response,component=app -n %NAMESPACE% --tail=20

echo.
echo [SUCCESS] 🎉 Emergency Response App deployed successfully!
echo.
echo [INFO] Useful commands:
echo   - View pods: kubectl get pods -n %NAMESPACE%
echo   - View services: kubectl get services -n %NAMESPACE%
echo   - View logs: kubectl logs -f deployment/emergency-response-app -n %NAMESPACE%
echo   - Scale app: kubectl scale deployment emergency-response-app --replicas=5 -n %NAMESPACE%
echo   - Port forward: kubectl port-forward service/emergency-response-nginx 8080:80 -n %NAMESPACE%
echo.
goto end

:cleanup
echo [WARNING] Cleaning up deployment...

if "%DEPLOYMENT_METHOD%"=="helm" (
    helm uninstall emergency-response -n %NAMESPACE%
) else (
    kubectl delete -f k8s/ --ignore-not-found=true
)

kubectl delete namespace %NAMESPACE% --ignore-not-found=true
echo [SUCCESS] Cleanup completed

:end
