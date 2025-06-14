# 📊 Prometheus & Grafana Monitoring Setup Guide

## 🎯 Overview
Complete guide for setting up monitoring and visualization for the Emergency Response App using Prometheus and Grafana.

## 🏗️ Architecture

```
Emergency Response App (Port 3000)
    ↓ (metrics endpoint /metrics)
Prometheus (Port 9090)
    ↓ (data source)
Grafana (Port 3001)
    ↓ (alerts)
Alertmanager (Port 9093)
```

## 🚀 Quick Start

### 1. Start Monitoring Stack
```bash
cd c:\Users\hp\Desktop\loopes\loope

# Start all monitoring services
docker-compose -f docker-compose.monitoring.yml up -d

# Check container status
docker ps
```

**Expected Containers**:
```
CONTAINER ID   IMAGE                    PORTS                    NAMES
abc123def456   prom/prometheus:latest   0.0.0.0:9090->9090/tcp   emergency-prometheus
def456ghi789   grafana/grafana:latest   0.0.0.0:3001->3000/tcp   emergency-grafana
ghi789jkl012   prom/alertmanager:latest 0.0.0.0:9093->9093/tcp   emergency-alertmanager
jkl012mno345   prom/node-exporter:latest 0.0.0.0:9100->9100/tcp  emergency-node-exporter
```

### 2. Verify Services
```bash
# Check Prometheus
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3001/api/health

# Check Emergency App metrics
curl http://localhost:3000/metrics
```

## 📈 Prometheus Setup & Usage

### Access Prometheus
- **URL**: http://localhost:9090
- **Purpose**: Metrics collection and alerting

### Key Features

#### 1. Targets Monitoring
Navigate to **Status > Targets** to see:
- ✅ `emergency-app` (localhost:3000) - UP
- ✅ `prometheus` (localhost:9090) - UP  
- ✅ `node-exporter` (localhost:9100) - UP

#### 2. Metrics Explorer
Go to **Graph** tab and try these queries:

```promql
# Emergency reports by severity
emergency_reports_total

# System health score
system_health_score

# Active users count
active_users

# HTTP request rate
rate(flask_http_request_total[5m])

# Response time percentiles
histogram_quantile(0.95, flask_http_request_duration_seconds_bucket)

# First aid guide views
first_aid_views_total

# Page views by page
page_views_total
```

#### 3. Alert Rules
Navigate to **Alerts** to see configured rules:
- 🚨 **HighEmergencyReports**: >5 reports in 5 minutes
- 🚨 **SystemHealthLow**: Health score <50
- 🚨 **AppDown**: App unreachable >1 minute
- 🚨 **HighResponseTime**: 95th percentile >2 seconds

### Custom Metrics Available

#### Application Metrics
```promql
# Emergency reports by severity
emergency_reports_total{severity="high"}
emergency_reports_total{severity="medium"}
emergency_reports_total{severity="low"}

# Page views by page type
page_views_total{page="landing"}
page_views_total{page="map"}
page_views_total{page="first_aid"}

# First aid practice views
first_aid_views_total{practice_id="1",practice_name="CPR"}
```

#### System Metrics
```promql
# System health (0-100)
system_health_score

# Active users
active_users

# Flask HTTP metrics
flask_http_request_total
flask_http_request_duration_seconds
```

## 📊 Grafana Dashboard Setup

### Access Grafana
- **URL**: http://localhost:3001
- **Username**: `admin`
- **Password**: `emergency123`

### Pre-configured Dashboard

#### 1. Emergency Response App Dashboard
Navigate to **Dashboards > Emergency Response App Dashboard**

**Panels Include**:
1. **Emergency Reports Rate** (Time Series)
   - Shows rate of emergency reports over time
   - Query: `rate(emergency_reports_total[5m])`

2. **System Health Score** (Gauge)
   - Visual health indicator (0-100%)
   - Query: `system_health_score`
   - Thresholds: Red <50, Yellow 50-80, Green >80

3. **Emergency Reports by Severity** (Pie Chart)
   - Distribution of reports by severity level
   - Query: `emergency_reports_total`

4. **Active Users** (Stat Panel)
   - Current number of active users
   - Query: `active_users`

#### 2. Creating Custom Dashboards

**Step 1**: Click **+ > Dashboard**

**Step 2**: Add Panel with these queries:
```promql
# Response Time Panel
histogram_quantile(0.95, flask_http_request_duration_seconds_bucket)

# Error Rate Panel
rate(flask_http_request_total{status=~"4..|5.."}[5m])

# First Aid Views Panel
sum(rate(first_aid_views_total[5m])) by (practice_name)
```

**Step 3**: Configure visualization:
- **Panel Type**: Time series, Gauge, Stat, Pie chart
- **Time Range**: Last 1 hour, 6 hours, 24 hours
- **Refresh**: 5s, 10s, 30s, 1m

### Alert Configuration

#### 1. Create Alert Rules
Navigate to **Alerting > Alert Rules > New Rule**

**Example Alert**: High Emergency Reports
```yaml
Query: increase(emergency_reports_total[5m]) > 5
Condition: IS ABOVE 5
Evaluation: Every 1m for 2m
```

#### 2. Notification Channels
Go to **Alerting > Notification Channels**

**Email Notifications**:
```yaml
Type: Email
Email addresses: admin@emergency-app.com
Subject: Emergency App Alert
Message: Alert: {{ .CommonAnnotations.summary }}
```

**Webhook Notifications**:
```yaml
Type: Webhook
URL: http://localhost:3000/api/v1/alerts
HTTP Method: POST
```

## 🚨 Alertmanager Configuration

### Access Alertmanager
- **URL**: http://localhost:9093
- **Purpose**: Alert routing and notifications

### Alert Routing
Configured in `monitoring/alertmanager.yml`:

```yaml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://host.docker.internal:3000/api/v1/alerts'
```

### Testing Alerts

#### 1. Trigger Test Alert
```bash
# Create high load to trigger alerts
for i in {1..10}; do
  curl -X POST \
    -H "Content-Type: application/json" \
    -H "X-API-Key: emergency-api-key-2024" \
    -d '{"emergency_type":"test","location":"Test","description":"Load test","severity":"high"}' \
    http://localhost:3000/api/v1/emergencies
done
```

#### 2. View Active Alerts
- Go to http://localhost:9093
- Check **Alerts** tab for active alerts
- Verify alert grouping and routing

## 🔧 Advanced Configuration

### Custom Metrics in Application

Add to your Flask app:
```python
from prometheus_client import Counter, Histogram, Gauge

# Custom metrics
CUSTOM_COUNTER = Counter('custom_events_total', 'Custom events', ['event_type'])
RESPONSE_TIME = Histogram('custom_response_time_seconds', 'Response time')
QUEUE_SIZE = Gauge('queue_size', 'Current queue size')

# Usage in routes
@app.route('/custom-endpoint')
def custom_endpoint():
    CUSTOM_COUNTER.labels(event_type='api_call').inc()
    with RESPONSE_TIME.time():
        # Your code here
        return jsonify({'status': 'success'})
```

### Prometheus Configuration

Edit `monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'emergency-app'
    static_configs:
      - targets: ['host.docker.internal:3000']
    scrape_interval: 10s
    metrics_path: '/metrics'
```

### Grafana Provisioning

Auto-provision dashboards in `monitoring/grafana/provisioning/`:

**datasources/prometheus.yml**:
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
```

## 📊 Monitoring Best Practices

### 1. Metric Naming
- Use descriptive names: `emergency_reports_total` not `reports`
- Include units: `response_time_seconds` not `response_time`
- Use consistent labels: `{severity="high"}` not `{level="high"}`

### 2. Dashboard Design
- Group related metrics together
- Use appropriate visualization types
- Set meaningful time ranges
- Add descriptions and units

### 3. Alert Configuration
- Set appropriate thresholds
- Avoid alert fatigue
- Group related alerts
- Test alert delivery

### 4. Performance Optimization
- Limit metric cardinality
- Use recording rules for complex queries
- Set appropriate retention periods
- Monitor Prometheus resource usage

## 🔍 Troubleshooting

### Common Issues

#### 1. Metrics Not Appearing
```bash
# Check if app is exposing metrics
curl http://localhost:3000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

#### 2. Grafana Can't Connect to Prometheus
```bash
# Check Docker network
docker network ls
docker network inspect loope_monitoring

# Test connectivity
docker exec emergency-grafana curl http://prometheus:9090/api/v1/query?query=up
```

#### 3. Alerts Not Firing
```bash
# Check alert rules
curl http://localhost:9090/api/v1/rules

# Check Alertmanager
curl http://localhost:9093/api/v1/alerts
```

### Log Analysis
```bash
# Prometheus logs
docker logs emergency-prometheus

# Grafana logs
docker logs emergency-grafana

# Alertmanager logs
docker logs emergency-alertmanager
```

## 📈 Monitoring Metrics Reference

### Emergency App Metrics
| Metric | Type | Description |
|--------|------|-------------|
| `emergency_reports_total` | Counter | Total emergency reports by severity |
| `system_health_score` | Gauge | System health score (0-100) |
| `active_users` | Gauge | Current active users |
| `page_views_total` | Counter | Page views by page type |
| `first_aid_views_total` | Counter | First aid guide views |
| `flask_http_request_total` | Counter | HTTP requests by method/status |
| `flask_http_request_duration_seconds` | Histogram | HTTP request duration |

### System Metrics (Node Exporter)
| Metric | Description |
|--------|-------------|
| `node_cpu_seconds_total` | CPU usage |
| `node_memory_MemAvailable_bytes` | Available memory |
| `node_filesystem_avail_bytes` | Available disk space |
| `node_load1` | 1-minute load average |

## 🎯 Success Indicators

### Healthy Monitoring Stack
- ✅ All containers running
- ✅ Prometheus targets UP
- ✅ Grafana dashboards loading
- ✅ Metrics being collected
- ✅ Alerts configured and testable

### Key Performance Indicators
- **Uptime**: >99.9%
- **Response Time**: <2 seconds (95th percentile)
- **Error Rate**: <1%
- **Alert Response**: <1 minute
- **Dashboard Load Time**: <5 seconds

---

**🎉 Your monitoring stack is now fully operational!**

Access your monitoring services:
- 📊 **Grafana Dashboard**: http://localhost:3001 (admin/emergency123)
- 📈 **Prometheus**: http://localhost:9090
- 🚨 **Alertmanager**: http://localhost:9093
- 📱 **Emergency App**: http://localhost:3000
