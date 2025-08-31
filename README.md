# Kubernetes Health Monitoring System

An automated health monitoring system for Kubernetes clusters with self-healing capabilities, real-time alerts, and a web dashboard.

## Project Goals

1. **Automated Health Monitoring**: Monitor key metrics like node health, pod statuses, and resource utilization
2. **Self-Healing Actions**: Restart failed pods, reschedule workloads, and trigger scaling events
3. **Real-time Alerts**: Provide notifications for critical issues requiring manual intervention
4. **Web Dashboard**: Display real-time health status, historical data, and auto-healing logs

## Architecture

- **Monitor Service**: Core monitoring and metrics collection
- **Healing Service**: Automated self-healing actions
- **Alert Service**: Real-time notifications and alerting
- **Dashboard**: Web interface for visualization and management
- **Database**: Store historical data and logs

## Quick Start

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure Kubernetes access (if running outside cluster)
kubectl config current-context

# Run the monitoring system
python -m src.main
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd dashboard-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t k8s-health-monitor .

# Run with Docker
docker run -p 8000:8000 -v ~/.kube/config:/root/.kube/config k8s-health-monitor
```

### Kubernetes Deployment

```bash
# Apply RBAC permissions
kubectl apply -f k8s/rbac.yaml

# Deploy the application
kubectl apply -f k8s/deployment.yaml

# Optional: Apply ingress
kubectl apply -f k8s/ingress.yaml
```

## Configuration

The system is configured via `config/config.yaml`. Key settings include:

- **Kubernetes**: Connection settings and namespace filtering
- **Monitoring**: Polling intervals and metrics to collect
- **Healing**: Self-healing thresholds and enabled actions
- **Alerts**: Notification channels and severity levels
- **Dashboard**: Web server settings and authentication

## Features

### Monitoring
- Node health and resource capacity
- Pod status and restart counts
- Deployment replica status
- Real-time metrics collection
- Historical data storage

### Self-Healing
- Automatic pod restart for failed pods
- Rescheduling of stuck pending pods
- Deployment scaling based on thresholds
- Configurable safety limits and thresholds

### Alerting
- Multiple notification channels (log, webhook, email)
- Severity-based filtering
- Alert deduplication and management
- Integration with external systems

### Dashboard
- Real-time system status overview
- Interactive charts and metrics
- Historical data visualization
- Self-healing action logs
- System configuration management

## API Endpoints

- `GET /` - System information
- `GET /health` - Health check
- `GET /api/status` - Overall system status
- `GET /api/metrics/nodes` - Node metrics
- `GET /api/metrics/pods` - Pod metrics
- `GET /api/events` - Cluster events
- `GET /api/healing-actions` - Healing action history
- `GET /api/alerts` - Active alerts
- `GET /api/config` - System configuration
- `WebSocket /api/ws` - Real-time updates

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
