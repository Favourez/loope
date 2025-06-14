#!/bin/bash
# Emergency Response App - Ansible Deployment Script

set -e

echo "=== Emergency Response App Infrastructure Deployment ==="
echo "Starting deployment at $(date)"

# Check if Ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo "Error: Ansible is not installed. Please install Ansible first."
    echo "Ubuntu/Debian: sudo apt install ansible"
    echo "CentOS/RHEL: sudo yum install ansible"
    echo "macOS: brew install ansible"
    exit 1
fi

# Change to ansible directory
cd "$(dirname "$0")"

echo "Current directory: $(pwd)"
echo "Available playbooks:"
ls -la *.yml

# Run syntax check
echo ""
echo "=== Running Ansible Syntax Check ==="
ansible-playbook --syntax-check site.yml

# Run dry run (check mode)
echo ""
echo "=== Running Dry Run (Check Mode) ==="
ansible-playbook --check site.yml

# Ask for confirmation
echo ""
read -p "Do you want to proceed with the actual deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Run actual deployment
echo ""
echo "=== Running Actual Deployment ==="
ansible-playbook site.yml -v

echo ""
echo "=== Deployment Summary ==="
echo "Deployment completed at $(date)"
echo ""
echo "Services should be available at:"
echo "- Emergency App: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3001 (admin/emergency123)"
echo "- Alertmanager: http://localhost:9093"
echo ""
echo "API Documentation: http://localhost:3000/api/v1/health"
echo ""
echo "To check service status:"
echo "  sudo systemctl status emergency-app"
echo "  docker ps"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u emergency-app -f"
echo "  tail -f /var/log/emergency-app/app.log"
