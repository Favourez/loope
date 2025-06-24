#!/bin/bash

# Emergency Response App - Kubernetes Deployment Script
# Deploys the application using Kubernetes manifests or Helm charts

set -e

echo "🚀 DEPLOYING EMERGENCY RESPONSE APP TO KUBERNETES"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Configuration
NAMESPACE="emergency-response"
DEPLOYMENT_METHOD=${1:-"helm"}  # helm or kubectl
ENVIRONMENT=${2:-"development"}  # development, staging, production

print_status "Deployment method: $DEPLOYMENT_METHOD"
print_status "Environment: $ENVIRONMENT"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

print_success "Connected to Kubernetes cluster"

# Function to deploy using kubectl
deploy_with_kubectl() {
    print_status "Deploying with kubectl..."
    
    # Create namespace
    print_status "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply manifests in order
    print_status "Applying Kubernetes manifests..."
    
    # 1. Namespace and RBAC
    kubectl apply -f k8s/namespace.yaml
    
    # 2. Secrets and ConfigMaps
    kubectl apply -f k8s/secrets.yaml
    kubectl apply -f k8s/configmap.yaml
    
    # 3. Persistent Volumes
    kubectl apply -f k8s/persistent-volumes.yaml
    
    # 4. Services
    kubectl apply -f k8s/services.yaml
    
    # 5. Deployments
    kubectl apply -f k8s/deployments.yaml
    
    # 6. HPA
    kubectl apply -f k8s/hpa.yaml
    
    # 7. Ingress
    kubectl apply -f k8s/ingress.yaml
    
    print_success "All manifests applied successfully"
}

# Function to deploy using Helm
deploy_with_helm() {
    print_status "Deploying with Helm..."
    
    # Check if Helm is available
    if ! command -v helm &> /dev/null; then
        print_error "Helm is not installed or not in PATH"
        exit 1
    fi
    
    # Create namespace
    print_status "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Add required Helm repositories
    print_status "Adding Helm repositories..."
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # Deploy with Helm
    print_status "Installing Emergency Response App with Helm..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        VALUES_FILE="helm/emergency-response/values-production.yaml"
    elif [ "$ENVIRONMENT" = "staging" ]; then
        VALUES_FILE="helm/emergency-response/values-staging.yaml"
    else
        VALUES_FILE="helm/emergency-response/values.yaml"
    fi
    
    # Check if values file exists, create if not
    if [ ! -f "$VALUES_FILE" ]; then
        print_warning "Values file $VALUES_FILE not found, using default values.yaml"
        VALUES_FILE="helm/emergency-response/values.yaml"
    fi
    
    helm upgrade --install emergency-response ./helm/emergency-response \
        --namespace $NAMESPACE \
        --values $VALUES_FILE \
        --wait \
        --timeout 10m
    
    print_success "Helm deployment completed successfully"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Wait for pods to be ready
    print_status "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=emergency-response --namespace=$NAMESPACE --timeout=300s
    
    # Check deployment status
    print_status "Checking deployment status..."
    kubectl get deployments -n $NAMESPACE
    kubectl get pods -n $NAMESPACE
    kubectl get services -n $NAMESPACE
    
    # Check if HPA is working
    if kubectl get hpa -n $NAMESPACE &> /dev/null; then
        print_status "HPA status:"
        kubectl get hpa -n $NAMESPACE
    fi
    
    # Get service URLs
    print_status "Service URLs:"
    
    # Get LoadBalancer IP (if available)
    EXTERNAL_IP=$(kubectl get service emergency-response-nginx -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [ -z "$EXTERNAL_IP" ]; then
        # Try to get NodePort
        NODE_PORT=$(kubectl get service emergency-response-nginx -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "")
        if [ ! -z "$NODE_PORT" ]; then
            NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}' 2>/dev/null || kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
            print_success "Application URL: http://$NODE_IP:$NODE_PORT"
        else
            print_warning "No external access configured. Use port-forward to access the application:"
            print_warning "kubectl port-forward service/emergency-response-nginx 8080:80 -n $NAMESPACE"
        fi
    else
        print_success "Application URL: http://$EXTERNAL_IP"
    fi
    
    # Monitoring URLs
    print_status "Monitoring URLs:"
    print_status "- Grafana: kubectl port-forward service/emergency-response-grafana 3000:3000 -n $NAMESPACE"
    print_status "- Prometheus: kubectl port-forward service/emergency-response-prometheus 9090:9090 -n $NAMESPACE"
    
    print_success "Deployment verification completed"
}

# Function to show logs
show_logs() {
    print_status "Recent application logs:"
    kubectl logs -l app.kubernetes.io/name=emergency-response,component=app -n $NAMESPACE --tail=20
}

# Function to cleanup
cleanup() {
    print_warning "Cleaning up deployment..."
    
    if [ "$DEPLOYMENT_METHOD" = "helm" ]; then
        helm uninstall emergency-response -n $NAMESPACE
    else
        kubectl delete -f k8s/ --ignore-not-found=true
    fi
    
    kubectl delete namespace $NAMESPACE --ignore-not-found=true
    print_success "Cleanup completed"
}

# Main deployment logic
case "$DEPLOYMENT_METHOD" in
    "helm")
        deploy_with_helm
        ;;
    "kubectl")
        deploy_with_kubectl
        ;;
    "cleanup")
        cleanup
        exit 0
        ;;
    *)
        print_error "Invalid deployment method. Use 'helm', 'kubectl', or 'cleanup'"
        exit 1
        ;;
esac

# Verify deployment
verify_deployment

# Show logs
show_logs

echo ""
print_success "🎉 Emergency Response App deployed successfully!"
echo ""
print_status "Useful commands:"
echo "  - View pods: kubectl get pods -n $NAMESPACE"
echo "  - View services: kubectl get services -n $NAMESPACE"
echo "  - View logs: kubectl logs -f deployment/emergency-response-app -n $NAMESPACE"
echo "  - Scale app: kubectl scale deployment emergency-response-app --replicas=5 -n $NAMESPACE"
echo "  - Port forward: kubectl port-forward service/emergency-response-nginx 8080:80 -n $NAMESPACE"
echo ""
