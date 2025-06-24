# Emergency Response App - VPS Deployment Script (PowerShell)
# This script deploys the application to the VPS using Kubernetes and Helm

param(
    [string]$VpsHost = "31.97.11.49",
    [string]$VpsUser = "root",
    [string]$VpsPassword = "Sofware-2025",
    [string]$RegistryPort = "32000",
    [string]$AppPort = "8888"
)

Write-Host "🚀 Starting VPS Deployment Process..." -ForegroundColor Green

# Function to create SSH session
function New-SSHSession {
    param($ComputerName, $Credential)
    try {
        $session = New-PSSession -ComputerName $ComputerName -Credential $Credential -ErrorAction Stop
        return $session
    }
    catch {
        Write-Host "❌ Failed to create SSH session: $_" -ForegroundColor Red
        return $null
    }
}

# Create credentials
$securePassword = ConvertTo-SecureString $VpsPassword -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($VpsUser, $securePassword)

Write-Host "📦 Step 1: Saving Docker images locally..." -ForegroundColor Yellow
docker save emergency-response-app:v1.0.0 | gzip > emergency-app.tar.gz
docker save monitoring-dashboard:v1.0.0 | gzip > monitoring-dashboard.tar.gz  
docker save nginx-proxy:v1.0.0 | gzip > nginx-proxy.tar.gz

Write-Host "📤 Step 2: Transferring files to VPS using SCP..." -ForegroundColor Yellow

# Use SCP to transfer files (requires OpenSSH client)
$scpCommands = @(
    "scp -o StrictHostKeyChecking=no emergency-app.tar.gz ${VpsUser}@${VpsHost}:/tmp/",
    "scp -o StrictHostKeyChecking=no monitoring-dashboard.tar.gz ${VpsUser}@${VpsHost}:/tmp/",
    "scp -o StrictHostKeyChecking=no nginx-proxy.tar.gz ${VpsUser}@${VpsHost}:/tmp/",
    "scp -o StrictHostKeyChecking=no -r helm/ ${VpsUser}@${VpsHost}:/tmp/",
    "scp -o StrictHostKeyChecking=no -r k8s/ ${VpsUser}@${VpsHost}:/tmp/"
)

foreach ($cmd in $scpCommands) {
    Write-Host "Executing: $cmd" -ForegroundColor Cyan
    $env:SSHPASS = $VpsPassword
    Invoke-Expression $cmd
}

Write-Host "🐳 Step 3: Executing deployment commands on VPS..." -ForegroundColor Yellow

# SSH commands to execute on VPS
$sshCommands = @(
    "cd /tmp && gunzip -c emergency-app.tar.gz | docker load",
    "cd /tmp && gunzip -c monitoring-dashboard.tar.gz | docker load", 
    "cd /tmp && gunzip -c nginx-proxy.tar.gz | docker load",
    "docker tag emergency-response-app:v1.0.0 localhost:${RegistryPort}/emergency-response-app:v1.0.0",
    "docker tag monitoring-dashboard:v1.0.0 localhost:${RegistryPort}/monitoring-dashboard:v1.0.0",
    "docker tag nginx-proxy:v1.0.0 localhost:${RegistryPort}/nginx-proxy:v1.0.0",
    "docker push localhost:${RegistryPort}/emergency-response-app:v1.0.0",
    "docker push localhost:${RegistryPort}/monitoring-dashboard:v1.0.0", 
    "docker push localhost:${RegistryPort}/nginx-proxy:v1.0.0",
    "alias kubectl='microk8s kubectl' && kubectl create namespace emergency-response --dry-run=client -o yaml | kubectl apply -f -",
    "cd /tmp && alias kubectl='microk8s kubectl' && microk8s helm3 install emergency-response helm/emergency-response/ --namespace emergency-response --set nginx.service.type=LoadBalancer --set nginx.service.port=${AppPort} --set app.image.repository=localhost:${RegistryPort}/emergency-response-app --set monitoring.image.repository=localhost:${RegistryPort}/monitoring-dashboard --set nginx.image.repository=localhost:${RegistryPort}/nginx-proxy",
    "alias kubectl='microk8s kubectl' && kubectl wait --for=condition=available --timeout=300s deployment --all -n emergency-response",
    "alias kubectl='microk8s kubectl' && kubectl get all -n emergency-response",
    "alias kubectl='microk8s kubectl' && kubectl get services -n emergency-response"
)

foreach ($cmd in $sshCommands) {
    Write-Host "Executing on VPS: $cmd" -ForegroundColor Cyan
    $env:SSHPASS = $VpsPassword
    $sshCmd = "ssh -o StrictHostKeyChecking=no ${VpsUser}@${VpsHost} `"$cmd`""
    Invoke-Expression $sshCmd
}

Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "🌐 Application should be accessible at: http://${VpsHost}:${AppPort}" -ForegroundColor Green
Write-Host "📊 Monitoring dashboard at: http://${VpsHost}:${AppPort}/monitoring" -ForegroundColor Green

# Cleanup
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Path "emergency-app.tar.gz", "monitoring-dashboard.tar.gz", "nginx-proxy.tar.gz" -ErrorAction SilentlyContinue

$env:SSHPASS = $VpsPassword
$cleanupCmd = "ssh -o StrictHostKeyChecking=no ${VpsUser}@${VpsHost} `"rm -f /tmp/*.tar.gz`""
Invoke-Expression $cleanupCmd

Write-Host "🎉 VPS Deployment Complete!" -ForegroundColor Green
