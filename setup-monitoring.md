# Emergency Response App - Monitoring Setup

## 📊 Prometheus and Grafana Monitoring

This document explains how to set up comprehensive monitoring for the Emergency Response App using Prometheus and Grafana.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the services:**
   - **Emergency App**: http://localhost:3000
   - **Prometheus**: http://localhost:9090
   - **Grafana**: http://localhost:3001 (admin/admin123)
   - **AlertManager**: http://localhost:9093

### Option 2: Manual Setup

1. **Install Prometheus:**
   ```bash
   # Download and extract Prometheus
   wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.windows-amd64.zip
   unzip prometheus-2.45.0.windows-amd64.zip
   cd prometheus-2.45.0.windows-amd64
   
   # Copy our configuration
   copy ..\prometheus.yml .
   copy ..\alert_rules.yml .
   
   # Start Prometheus
   prometheus.exe --config.file=prometheus.yml
   ```

2. **Install Grafana:**
   ```bash
   # Download and extract Grafana
   wget https://dl.grafana.com/oss/release/grafana-10.0.0.windows-amd64.zip
   unzip grafana-10.0.0.windows-amd64.zip
   cd grafana-10.0.0
   
   # Start Grafana
   bin\grafana-server.exe
   ```

## 📈 Metrics Available

### Application Metrics

1. **Emergency Reports**
   - `emergency_reports_total` - Total emergency reports by severity and type
   - Rate of emergency reports over time
   - Distribution by severity (low, medium, high, critical)

2. **First Aid Usage**
   - `first_aid_views_total` - Views of first aid guides by practice
   - Most accessed first aid procedures
   - User engagement with educational content

3. **Page Views**
   - `page_views_total` - Page views by page name
   - User navigation patterns
   - Popular sections of the app

4. **System Health**
   - `system_health_score` - Overall system health (0-100)
   - `active_users` - Number of active users
   - Response times and error rates

### Infrastructure Metrics (with Node Exporter)

1. **System Resources**
   - CPU usage
   - Memory usage
   - Disk space
   - Network I/O

2. **Application Performance**
   - HTTP request duration
   - Request rate
   - Error rate
   - Response codes

## 🚨 Alerts Configured

### Critical Alerts
- **CriticalEmergencyReports**: Immediate notification for critical emergencies
- **ApplicationDown**: App unavailability
- **SystemHealthCritical**: System health below 50%

### Warning Alerts
- **HighEmergencyReports**: More than 5 reports in 5 minutes
- **SystemHealthLow**: System health below 70%
- **HighResponseTime**: 95th percentile > 2 seconds
- **HighErrorRate**: Error rate > 0.1 per second

### Infrastructure Alerts
- **HighCPUUsage**: CPU > 80% for 5 minutes
- **HighMemoryUsage**: Memory > 85% for 5 minutes

## 📊 Grafana Dashboards

### Emergency Response Dashboard
- **Emergency Reports Rate**: Real-time emergency reporting trends
- **System Health Gauge**: Visual health indicator
- **Page Views Distribution**: User engagement pie chart
- **Active Users**: Current user count
- **First Aid Usage**: Most accessed guides

### Key Panels:
1. **Emergency Metrics**
   - Reports by severity over time
   - Geographic distribution (if location data available)
   - Response time metrics

2. **User Engagement**
   - Page views and navigation patterns
   - First aid guide popularity
   - Session duration and bounce rate

3. **System Performance**
   - Response times and throughput
   - Error rates and status codes
   - Resource utilization

## 🔧 Configuration Files

### Prometheus Configuration (`prometheus.yml`)
- Scrapes metrics from the Flask app every 5 seconds
- Includes alerting rules for emergency scenarios
- Monitors system metrics via Node Exporter

### Alert Rules (`alert_rules.yml`)
- Emergency-specific alerts for critical situations
- Performance and availability monitoring
- Escalation policies for different severity levels

### Grafana Provisioning
- Automatic dashboard and datasource setup
- Pre-configured emergency response dashboard
- Custom panels for emergency metrics

## 🔍 Monitoring Endpoints

### Application Endpoints
- `/health` - Health check with system status
- `/metrics` - Prometheus metrics endpoint
- `/webhook/alerts` - AlertManager webhook (optional)

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-05-25T22:52:45.915023",
  "version": "1.0.0",
  "active_users": 1,
  "total_emergency_reports": 0,
  "system_health_score": 94.5
}
```

## 🚨 Emergency Response Integration

### Real-time Monitoring
- Immediate alerts for critical emergency reports
- System health degradation monitoring
- Performance impact assessment during emergencies

### Escalation Procedures
1. **Critical Emergency**: Instant notification to emergency responders
2. **System Issues**: Alert technical team for immediate resolution
3. **Performance Degradation**: Automatic scaling triggers (if configured)

## 📱 Mobile and Remote Access

### Grafana Mobile App
- Install Grafana mobile app for remote monitoring
- Configure push notifications for critical alerts
- Access dashboards from anywhere

### API Access
- Prometheus API for custom integrations
- Grafana API for programmatic dashboard management
- Health check endpoint for external monitoring

## 🔒 Security Considerations

### Authentication
- Grafana admin credentials: admin/admin123 (change in production)
- Prometheus basic auth (configure as needed)
- Network security and firewall rules

### Data Privacy
- Metrics anonymization for user data
- Retention policies for sensitive information
- Compliance with emergency service regulations

## 🛠️ Troubleshooting

### Common Issues
1. **Metrics not appearing**: Check Flask app `/metrics` endpoint
2. **Grafana connection issues**: Verify Prometheus datasource URL
3. **Alerts not firing**: Check AlertManager configuration and SMTP settings

### Debug Commands
```bash
# Check if metrics endpoint is working
curl http://localhost:3000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana health
curl http://localhost:3001/api/health
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Emergency Response Best Practices](https://www.ready.gov/)
- [Monitoring Emergency Systems](https://www.fema.gov/emergency-managers)

## 🎯 Next Steps

1. **Production Deployment**: Use proper WSGI server (Gunicorn/uWSGI)
2. **High Availability**: Set up Prometheus and Grafana clustering
3. **Advanced Alerting**: Integrate with PagerDuty, Slack, or SMS services
4. **Custom Dashboards**: Create role-specific dashboards for different users
5. **Log Aggregation**: Add ELK stack for comprehensive logging
