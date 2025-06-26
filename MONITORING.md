# 📊 Emergency Response App - Monitoring & Dashboards

## 🎯 Overview
Comprehensive monitoring solution for the Emergency Response Application using Prometheus and Grafana with real-time metrics, alerts, and dashboards.

## 🔧 Services & Access

### 📈 **Prometheus** (Metrics Collection)
- **URL**: http://31.97.11.49:9090
- **Purpose**: Collects and stores metrics from the Emergency Response App
- **Scrape Interval**: 5 seconds for app metrics, 10s for system metrics

### 📊 **Grafana** (Visualization & Dashboards)
- **URL**: http://31.97.11.49:3001
- **Username**: `admin`
- **Password**: `emergency123`
- **Purpose**: Visualizes metrics with interactive dashboards

## 🎛️ Available Dashboards

### 1. **Emergency Response App Dashboard** (Original)
- Basic metrics overview
- System health monitoring
- Emergency reports tracking

### 2. **🚨 Comprehensive Emergency Monitoring** (Enhanced)
- **Emergency Reports Total** with severity thresholds
- **System Health Score** gauge (0-100%)
- **Active Users** counter
- **Page Views** statistics
- **Emergency Reports by Severity** pie chart
- **First Aid Views by Practice** bar chart

### 3. **🔴 Real-Time Emergency Response Monitoring** (Live)
- **Live Emergency Reports Rate** (per minute)
- **Response Time Distribution** (50th, 95th, 99th percentiles)
- **Page Views Over Time** timeline
- **Emergency Reports Heatmap** by type & severity
- **First Aid Guide Usage** trends
- **Critical Alerts** panel

## 📊 Key Metrics Tracked

### 🚨 Emergency Metrics
- `emergency_reports_total` - Total emergency reports by severity and type
- `first_aid_views_total` - First aid guide views by practice
- `page_views_total` - Page views by endpoint
- `active_users` - Current active users count
- `system_health_score` - Overall system health (0-100)

### ⚡ Performance Metrics
- `response_time_seconds` - HTTP response time histogram
- `flask_http_request_duration_seconds` - Flask request duration
- `flask_http_request_total` - Total HTTP requests
- `process_resident_memory_bytes` - Memory usage

### 🔍 System Metrics
- `up` - Service availability
- `python_gc_*` - Python garbage collection metrics
- `process_*` - Process-level metrics

## 🚨 Alert Rules

### Critical Alerts
- **EmergencyAppDown**: App unavailable for >1 minute
- **SystemHealthCritical**: Health score <20 for >2 minutes

### Warning Alerts
- **HighEmergencyReports**: >10 reports in 5 minutes
- **SystemHealthLow**: Health score <50 for >5 minutes
- **HighResponseTime**: 95th percentile >2 seconds for >3 minutes
- **HighMemoryUsage**: Memory usage >500MB for >5 minutes

### Info Alerts
- **NoActiveUsers**: No users for >10 minutes

## 🎯 Monitoring Features

### Real-Time Monitoring
- **1-second refresh** for critical dashboards
- **Live metrics** from application endpoints
- **Instant alerting** on threshold breaches

### Historical Analysis
- **Time-series data** for trend analysis
- **Configurable time ranges** (15m, 1h, 6h, 24h, 7d)
- **Data retention** as per Prometheus configuration

### Interactive Dashboards
- **Drill-down capabilities** on all charts
- **Custom time range selection**
- **Export functionality** for reports
- **Mobile-responsive** design

## 🔧 Configuration Files

### Prometheus Configuration
- `monitoring/prometheus.yml` - Main Prometheus config
- `monitoring/alert_rules.yml` - Alert definitions

### Grafana Configuration
- `monitoring/grafana/provisioning/` - Auto-provisioning configs
- `monitoring/grafana/dashboards/` - Dashboard definitions

## 🧪 Testing & Load Generation

### Metrics Test Script
```bash
python monitoring/test-metrics.py
```

This script generates:
- Simulated page views
- Test emergency reports
- First aid guide interactions
- Health check requests
- Load testing scenarios

## 📱 Dashboard Access Guide

1. **Access Grafana**: http://31.97.11.49:3001
2. **Login**: admin / emergency123
3. **Navigate to Dashboards** → Browse
4. **Select Dashboard**:
   - "Emergency Response App Dashboard" (Basic)
   - "Emergency Response App - Comprehensive Monitoring" (Enhanced)
   - "🚨 Real-Time Emergency Response Monitoring" (Live)

## 🔍 Troubleshooting

### Common Issues
1. **No Data in Dashboards**
   - Check Prometheus targets: http://31.97.11.49:9090/targets
   - Verify app metrics: http://31.97.11.49/metrics

2. **Grafana Login Issues**
   - Use credentials: admin / emergency123
   - Check container status: `docker ps`

3. **Missing Metrics**
   - Restart monitoring services: `docker compose restart prometheus grafana`
   - Check application logs: `docker logs emergency-app-local`

## 🚀 Next Steps

1. **Custom Alerts**: Configure email/Slack notifications
2. **Extended Metrics**: Add business-specific KPIs
3. **Performance Optimization**: Based on monitoring insights
4. **Capacity Planning**: Using historical trend data
