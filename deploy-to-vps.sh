#!/bin/bash

# Emergency Response App - VPS Deployment Script
# This script deploys the application to the VPS using Kubernetes and Helm

set -e

VPS_HOST="31.97.11.49"
VPS_USER="root"
VPS_PASSWORD="Sofware-2025"
REGISTRY_PORT="32000"
APP_PORT="8888"

echo "🚀 Starting VPS Deployment Process..."

# Function to execute commands on VPS
execute_on_vps() {
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$1"
}

# Function to copy files to VPS
copy_to_vps() {
    sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$1" "$VPS_USER@$VPS_HOST:$2"
}

echo "📦 Step 1: Saving Docker images locally..."
docker save emergency-response-app:v1.0.0 | gzip > emergency-app.tar.gz
docker save monitoring-dashboard:v1.0.0 | gzip > monitoring-dashboard.tar.gz
docker save nginx-proxy:v1.0.0 | gzip > nginx-proxy.tar.gz

echo "📤 Step 2: Transferring images to VPS..."
copy_to_vps "emergency-app.tar.gz" "/tmp/"
copy_to_vps "monitoring-dashboard.tar.gz" "/tmp/"
copy_to_vps "nginx-proxy.tar.gz" "/tmp/"

echo "📤 Step 3: Transferring Helm charts to VPS..."
copy_to_vps "helm/" "/tmp/"
copy_to_vps "k8s/" "/tmp/"

echo "🐳 Step 4: Loading images on VPS..."
execute_on_vps "cd /tmp && gunzip -c emergency-app.tar.gz | docker load"
execute_on_vps "cd /tmp && gunzip -c monitoring-dashboard.tar.gz | docker load"
execute_on_vps "cd /tmp && gunzip -c nginx-proxy.tar.gz | docker load"

echo "🏷️ Step 5: Tagging images for local registry..."
execute_on_vps "docker tag emergency-response-app:v1.0.0 localhost:$REGISTRY_PORT/emergency-response-app:v1.0.0"
execute_on_vps "docker tag monitoring-dashboard:v1.0.0 localhost:$REGISTRY_PORT/monitoring-dashboard:v1.0.0"
execute_on_vps "docker tag nginx-proxy:v1.0.0 localhost:$REGISTRY_PORT/nginx-proxy:v1.0.0"

echo "📤 Step 6: Pushing images to local registry..."
execute_on_vps "docker push localhost:$REGISTRY_PORT/emergency-response-app:v1.0.0"
execute_on_vps "docker push localhost:$REGISTRY_PORT/monitoring-dashboard:v1.0.0"
execute_on_vps "docker push localhost:$REGISTRY_PORT/nginx-proxy:v1.0.0"

echo "🎯 Step 7: Creating namespace..."
execute_on_vps "alias kubectl='microk8s kubectl' && kubectl create namespace emergency-response --dry-run=client -o yaml | kubectl apply -f -"

echo "🚀 Step 8: Deploying with Helm..."
execute_on_vps "cd /tmp && alias kubectl='microk8s kubectl' && microk8s helm3 install emergency-response helm/emergency-response/ --namespace emergency-response --set nginx.service.type=LoadBalancer --set nginx.service.port=$APP_PORT --set app.image.repository=localhost:$REGISTRY_PORT/emergency-response-app --set monitoring.image.repository=localhost:$REGISTRY_PORT/monitoring-dashboard --set nginx.image.repository=localhost:$REGISTRY_PORT/nginx-proxy"

echo "⏳ Step 9: Waiting for deployment to be ready..."
execute_on_vps "alias kubectl='microk8s kubectl' && kubectl wait --for=condition=available --timeout=300s deployment --all -n emergency-response"

echo "🔍 Step 10: Getting deployment status..."
execute_on_vps "alias kubectl='microk8s kubectl' && kubectl get all -n emergency-response"

echo "🌐 Step 11: Getting service information..."
execute_on_vps "alias kubectl='microk8s kubectl' && kubectl get services -n emergency-response"

echo "✅ Deployment completed successfully!"
echo "🌐 Application should be accessible at: http://$VPS_HOST:$APP_PORT"
echo "📊 Monitoring dashboard at: http://$VPS_HOST:$APP_PORT/monitoring"

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -f emergency-app.tar.gz monitoring-dashboard.tar.gz nginx-proxy.tar.gz
execute_on_vps "rm -f /tmp/*.tar.gz"

echo "🎉 VPS Deployment Complete!"
