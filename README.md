# Kubernetes Health Monitoring System

An automated health monitoring system for Kubernetes clusters with self-healing capabilities, real-time alerts, Prometheus metrics, Grafana dashboards, and Slack notifications.

## Project Goals

1. **Automated Health Monitoring**: Monitor key metrics like node health, pod statuses, and resource utilization
2. **Self-Healing Actions**: Restart failed pods, reschedule workloads, and trigger scaling events
3. **Real-time Alerts**: Provide notifications for critical issues requiring manual intervention
4. **Web Dashboard**: Display real-time health status, historical data, and auto-healing logs
5. **Prometheus Integration**: Export metrics for advanced monitoring and alerting
6. **Grafana Visualization**: Pre-built dashboards for comprehensive cluster insights
7. **Slack Notifications**: Real-time alerts to DevOps teams

## Architecture

- **Monitor Service**: Core monitoring and metrics collection
- **Healing Service**: Automated self-healing actions
- **Alert Service**: Real-time notifications and alerting (Slack, webhook, email)
- **Dashboard**: Web interface for visualization and management
- **Database**: Store historical data and logs
- **Prometheus Exporter**: Export metrics in Prometheus format
- **Grafana Dashboards**: Advanced visualization and monitoring
- **Slack Integration**: Team notifications and alerts

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Kubernetes cluster (optional - runs in mock mode without cluster)
- Docker (optional, for containerized deployment)
- Docker Compose (for Prometheus/Grafana stack)

### Local Development

1. **Clone and setup**:
```bash
git clone <repository-url>
cd k8s-health-monitor
pip install -r requirements.txt
```

2. **Configure** (optional):
```bash
cp config/config.yaml.example config/config.yaml
# Edit configuration as needed
```

3. **Run the backend**:
```bash
python -m src.main
```

4. **Run the frontend** (in a separate terminal):
## 🐳 Docker Deployment

### Build and Run
```bash
docker build -t k8s-health-monitor .
docker run -p 8000:8000 k8s-health-monitor
```

### Full Stack with Prometheus & Grafana
```bash
# Run the complete monitoring stack
docker-compose -f docker-compose.prometheus.yml up -d

# Access services:
# - Application: http://localhost:8000
# - Prometheus: http://localhost:9090  
# - Grafana: http://localhost:3000 (admin/admin)
```

### Environment Variables
- `DATABASE_URL` - Database connection string
- `KUBECONFIG_PATH` - Path to kubeconfig file
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## ☸️ Kubernetes Deployment

### Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace k8s-health-monitor

# Apply RBAC permissions
kubectl apply -f k8s/rbac.yaml

# Deploy the application
kubectl apply -f k8s/deployment.yaml

# Deploy Prometheus
kubectl apply -f k8s/prometheus-deployment.yaml

# Deploy Grafana
kubectl apply -f k8s/grafana-deployment.yaml

# Setup ingress (optional)
kubectl apply -f k8s/ingress.yaml
```

### Access the Application
```bash
# Port forward to access locally
kubectl port-forward -n k8s-health-monitor service/k8s-health-monitor-service 8000:8000
kubectl port-forward -n k8s-health-monitor service/prometheus-service 9090:9090
kubectl port-forward -n k8s-health-monitor service/grafana-service 3000:3000

# Or access via ingress (configure your DNS)
# http://k8s-health-monitor.local
# http://prometheus.local
# http://grafana.local
```

## Configuration

The system is configured via `config/config.yaml`. Key settings include:

- **Kubernetes**: Connection settings and namespace filtering
- **Monitoring**: Polling intervals and metrics to collect
- **Healing**: Self-healing thresholds and enabled actions
- **Alerts**: Notification channels and severity levels
- **Dashboard**: Web server settings and authentication

## 🎯 Features

### ✅ Automated Health Monitoring
- **Node Monitoring**: Track node status, resource capacity, and conditions
- **Pod Monitoring**: Monitor pod health, restart counts, and readiness
- **Deployment Monitoring**: Watch deployment replica status and availability
- **Real-time Updates**: WebSocket-based live dashboard updates
- **Historical Data**: Store and query monitoring data over time
- **Prometheus Metrics**: Export metrics for advanced monitoring and alerting

### ✅ Self-Healing Capabilities  
- **Pod Restart**: Automatically restart failed or stuck pods
- **Workload Rescheduling**: Move pods from unhealthy nodes
- **Deployment Scaling**: Scale deployments based on resource utilization
- **Configurable Thresholds**: Customize healing triggers and limits
- **Safety Mechanisms**: Prevent runaway scaling and cascading failures

### ✅ Real-time Alerting
- **Multi-channel Notifications**: Log, webhook, email, and Slack alerts
- **Severity-based Filtering**: Configure alert levels and routing
- **Alert Deduplication**: Prevent alert spam and noise
- **Custom Templates**: Flexible alert message formatting
- **Integration Ready**: Slack, PagerDuty, and custom webhook support

### ✅ Web Dashboard & Visualization
- **Real-time Visualization**: Live cluster status and metrics
- **Interactive Charts**: Historical data with drill-down capabilities  
- **Healing Action Logs**: Track all automated interventions
- **System Configuration**: Manage settings through web interface
- **Responsive Design**: Works on desktop and mobile devices
- **Grafana Integration**: Pre-built dashboards for advanced visualization
- **Prometheus Metrics**: Industry-standard metrics collection and alerting

## 📊 API Endpoints

### Core Endpoints
- `GET /` - System information and status
- `GET /health` - Health check endpoint
- `GET /api/status` - Overall system status with metrics
- `GET /metrics` - Prometheus metrics endpoint

### Monitoring Data
- `GET /api/metrics/nodes` - Node health metrics
- `GET /api/metrics/pods` - Pod status and metrics  
- `GET /api/metrics/deployments` - Deployment status
- `GET /api/events` - Recent cluster events
- `GET /api/healing-actions` - Self-healing action history

### Real-time Updates
- `WebSocket /api/ws` - Real-time system status updates

### Prometheus Metrics
The `/metrics` endpoint exposes the following metrics:
- `k8s_node_status` - Node ready status (1=Ready, 0=NotReady)
- `k8s_node_cpu_capacity_cores` - Node CPU capacity
- `k8s_node_memory_capacity_bytes` - Node memory capacity
- `k8s_pod_status` - Pod running status (1=Running, 0=Other)
- `k8s_pod_restart_count_total` - Total pod restarts
- `k8s_pod_ready` - Pod ready status
- `k8s_cluster_events_total` - Cluster events by type and severity
- `k8s_healing_actions_total` - Healing actions by type and status
- `k8s_monitoring_cycles_total` - Total monitoring cycles completed
- `k8s_monitoring_cycle_duration_seconds` - Monitoring cycle duration

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_monitor.py
```

## Components

- `src/monitor/` - Core monitoring logic
- `src/healing/` - Self-healing automation
- `src/alerts/` - Alert and notification system
- `src/dashboard/` - Web dashboard API
- `src/database/` - Data persistence layer
- `dashboard-frontend/` - React frontend application
- `config/` - Configuration files
- `k8s/` - Kubernetes manifests
- `tests/` - Test suite

## Security Considerations

- RBAC permissions are minimal and scoped appropriately
- Database credentials should be stored securely
- Alert channel credentials (SMTP, webhooks) should use secrets
- Consider enabling authentication for production deployments

## Troubleshooting

### Common Issues

1. **Kubernetes Connection Failed**
   - Verify kubeconfig is accessible
   - Check RBAC permissions
   - Ensure cluster connectivity

2. **Database Connection Issues**
   - Check database file permissions (SQLite)
   - Verify PostgreSQL connection settings
   - Ensure data directory exists

3. **Frontend Not Loading**
   - Verify backend is running on port 8000
   - Check WebSocket connection
   - Ensure CORS is properly configured

4. **Self-Healing Not Working**
   - Check RBAC permissions for pod deletion
   - Verify healing is enabled in configuration
   - Review healing action logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.
