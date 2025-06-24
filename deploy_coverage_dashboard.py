#!/usr/bin/env python3
"""
Deploy Coverage Dashboard to VPS
Deploys the coverage dashboard to the production VPS server
"""

import paramiko
import os
import time
import subprocess

# VPS Configuration
VPS_HOST = "31.97.11.49"
VPS_USER = "root"
VPS_PASSWORD = "Software-2025"
DASHBOARD_PORT = 5001

def execute_ssh_command(ssh, command, description=""):
    """Execute SSH command on VPS"""
    if description:
        print(f"\n🔧 {description}")
    print(f"   Command: {command}")
    
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=120)
        exit_code = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if exit_code == 0:
            print(f"   ✅ Success")
            if output.strip():
                print(f"   Output: {output.strip()[:200]}...")
        else:
            print(f"   ❌ Failed (exit code: {exit_code})")
            if error.strip():
                print(f"   Error: {error.strip()}")
        
        return exit_code == 0, output, error
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False, "", str(e)

def upload_file(ssh, local_path, remote_path, description=""):
    """Upload file to VPS"""
    if description:
        print(f"\n📤 {description}")
    print(f"   Local: {local_path}")
    print(f"   Remote: {remote_path}")
    
    try:
        sftp = ssh.open_sftp()
        
        # Create remote directory if it doesn't exist
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.mkdir(remote_dir)
        except:
            pass  # Directory might already exist
        
        sftp.put(local_path, remote_path)
        sftp.close()
        
        print(f"   ✅ File uploaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        return False

def deploy_coverage_dashboard():
    """Deploy coverage dashboard to VPS"""
    print("🚀 DEPLOYING COVERAGE DASHBOARD TO VPS")
    print("=" * 60)
    print(f"Target: {VPS_HOST}:{DASHBOARD_PORT}")
    print("=" * 60)
    
    try:
        # Connect to VPS
        print("🔌 Connecting to VPS...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=30)
        print("✅ Connected to VPS successfully!")
        
        # Create application directory
        app_dir = "/opt/emergency-app"
        coverage_dir = f"{app_dir}/coverage"
        
        execute_ssh_command(ssh, f"mkdir -p {coverage_dir}", "Creating coverage directory")
        execute_ssh_command(ssh, f"mkdir -p {coverage_dir}/templates/coverage", "Creating templates directory")
        execute_ssh_command(ssh, f"mkdir -p {coverage_dir}/static/coverage", "Creating static directory")
        execute_ssh_command(ssh, f"mkdir -p {coverage_dir}/test-reports", "Creating test-reports directory")
        execute_ssh_command(ssh, f"mkdir -p {coverage_dir}/htmlcov", "Creating htmlcov directory")
        
        # Upload coverage dashboard files
        files_to_upload = [
            ('coverage_dashboard.py', f'{coverage_dir}/coverage_dashboard.py'),
            ('templates/coverage/coverage_dashboard.html', f'{coverage_dir}/templates/coverage/coverage_dashboard.html'),
            ('run_enhanced_coverage.py', f'{coverage_dir}/run_enhanced_coverage.py')
        ]
        
        for local_file, remote_file in files_to_upload:
            if os.path.exists(local_file):
                upload_file(ssh, local_file, remote_file, f"Uploading {local_file}")
            else:
                print(f"⚠️  Warning: {local_file} not found locally")
        
        # Upload coverage reports if they exist
        if os.path.exists('coverage.xml'):
            upload_file(ssh, 'coverage.xml', f'{coverage_dir}/coverage.xml', "Uploading coverage.xml")
        
        if os.path.exists('htmlcov/index.html'):
            upload_file(ssh, 'htmlcov/index.html', f'{coverage_dir}/htmlcov/index.html', "Uploading HTML coverage report")
        
        # Install Python dependencies
        execute_ssh_command(ssh, "python3 -m pip install flask flask-cors", "Installing Flask dependencies")
        
        # Create systemd service for coverage dashboard
        service_content = f"""[Unit]
Description=Emergency Response App Coverage Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={coverage_dir}
Environment=PYTHONPATH={coverage_dir}
ExecStart=/usr/bin/python3 {coverage_dir}/coverage_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        # Write service file
        execute_ssh_command(ssh, f"cat > /etc/systemd/system/coverage-dashboard.service << 'EOF'\n{service_content}\nEOF", "Creating systemd service")
        
        # Enable and start service
        execute_ssh_command(ssh, "systemctl daemon-reload", "Reloading systemd")
        execute_ssh_command(ssh, "systemctl enable coverage-dashboard", "Enabling coverage dashboard service")
        execute_ssh_command(ssh, "systemctl stop coverage-dashboard", "Stopping existing service")
        execute_ssh_command(ssh, "systemctl start coverage-dashboard", "Starting coverage dashboard service")
        
        # Configure firewall
        execute_ssh_command(ssh, f"ufw allow {DASHBOARD_PORT}", f"Opening port {DASHBOARD_PORT}")
        
        # Check service status
        execute_ssh_command(ssh, "systemctl status coverage-dashboard --no-pager", "Checking service status")
        
        # Create nginx configuration for reverse proxy (optional)
        nginx_config = f"""server {{
    listen 80;
    server_name coverage.{VPS_HOST};
    
    location / {{
        proxy_pass http://localhost:{DASHBOARD_PORT};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        execute_ssh_command(ssh, f"cat > /etc/nginx/sites-available/coverage-dashboard << 'EOF'\n{nginx_config}\nEOF", "Creating nginx configuration")
        execute_ssh_command(ssh, "ln -sf /etc/nginx/sites-available/coverage-dashboard /etc/nginx/sites-enabled/", "Enabling nginx site")
        execute_ssh_command(ssh, "nginx -t", "Testing nginx configuration")
        execute_ssh_command(ssh, "systemctl reload nginx", "Reloading nginx")
        
        # Create update script
        update_script = f"""#!/bin/bash
# Coverage Dashboard Update Script

echo "🔄 Updating Coverage Dashboard..."

# Navigate to coverage directory
cd {coverage_dir}

# Run coverage analysis
python3 run_enhanced_coverage.py

# Restart dashboard service
systemctl restart coverage-dashboard

echo "✅ Coverage dashboard updated!"
echo "📊 Dashboard URL: http://{VPS_HOST}:{DASHBOARD_PORT}"
"""
        
        execute_ssh_command(ssh, f"cat > {coverage_dir}/update_coverage.sh << 'EOF'\n{update_script}\nEOF", "Creating update script")
        execute_ssh_command(ssh, f"chmod +x {coverage_dir}/update_coverage.sh", "Making update script executable")
        
        ssh.close()
        
        print("\n" + "=" * 60)
        print("🎉 COVERAGE DASHBOARD DEPLOYMENT COMPLETED!")
        print("=" * 60)
        print(f"📊 Dashboard URL: http://{VPS_HOST}:{DASHBOARD_PORT}")
        print(f"📊 Alternative URL: http://srv878357.hstgr.cloud:{DASHBOARD_PORT}")
        print(f"🔧 Service: systemctl status coverage-dashboard")
        print(f"📝 Update: {coverage_dir}/update_coverage.sh")
        print("=" * 60)
        
        # Test dashboard accessibility
        print("\n🧪 Testing dashboard accessibility...")
        time.sleep(5)
        
        try:
            import requests
            response = requests.get(f"http://{VPS_HOST}:{DASHBOARD_PORT}", timeout=10)
            if response.status_code == 200:
                print("✅ Dashboard is accessible!")
            else:
                print(f"⚠️  Dashboard returned status: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Could not test dashboard: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def create_coverage_cron_job():
    """Create cron job for automatic coverage updates"""
    print("\n⏰ Setting up automatic coverage updates...")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=30)
        
        # Create cron job to update coverage daily
        cron_job = f"0 2 * * * /opt/emergency-app/coverage/update_coverage.sh >> /var/log/coverage-update.log 2>&1"
        
        execute_ssh_command(ssh, f"(crontab -l 2>/dev/null; echo '{cron_job}') | crontab -", "Adding cron job for daily coverage updates")
        
        ssh.close()
        print("✅ Automatic coverage updates configured (daily at 2 AM)")
        
    except Exception as e:
        print(f"⚠️  Could not set up cron job: {e}")

def main():
    """Main deployment function"""
    print("🚀 COVERAGE DASHBOARD DEPLOYMENT")
    print("=" * 80)
    
    # Deploy dashboard
    success = deploy_coverage_dashboard()
    
    if success:
        # Set up automatic updates
        create_coverage_cron_job()
        
        print("\n🎊 DEPLOYMENT SUCCESSFUL!")
        print("\n📋 NEXT STEPS:")
        print("1. Access dashboard: http://31.97.11.49:5001")
        print("2. Run coverage analysis on VPS")
        print("3. Monitor coverage metrics")
        print("4. Set up team access")
        
        print("\n🔧 MANAGEMENT COMMANDS:")
        print("• Check status: systemctl status coverage-dashboard")
        print("• View logs: journalctl -u coverage-dashboard -f")
        print("• Update coverage: /opt/emergency-app/coverage/update_coverage.sh")
        print("• Restart service: systemctl restart coverage-dashboard")
        
    else:
        print("\n💥 DEPLOYMENT FAILED!")
        print("Check the error messages above and try again.")
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
