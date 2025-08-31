"""
Tests for the API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.main import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Kubernetes Health Monitoring System"


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch('src.dashboard.api.db_manager')
def test_status_endpoint(mock_db, client):
    """Test system status endpoint"""
    mock_db.get_recent_node_metrics.return_value = []
    mock_db.get_recent_pod_metrics.return_value = []
    mock_db.get_recent_events.return_value = []
    mock_db.get_recent_healing_actions.return_value = []
    mock_db.get_active_alerts.return_value = []
    
    response = client.get("/api/status")
    assert response.status_code == 200
    
    data = response.json()
    assert 'nodes' in data
    assert 'pods' in data
    assert 'events' in data
    assert 'healing_actions' in data
    assert 'alerts' in data


@patch('src.dashboard.api.config')
def test_config_endpoint(mock_config, client):
    """Test configuration endpoint"""
    mock_config.get_kubernetes_config.return_value = {'in_cluster': False}
    mock_config.get_monitoring_config.return_value = {'interval': 30}
    mock_config.get_healing_config.return_value = {'enabled': True}
    mock_config.get_alerts_config.return_value = {'enabled': True}
    mock_config.get_dashboard_config.return_value = {'port': 8000}
    
    response = client.get("/api/config")
    assert response.status_code == 200
    
    data = response.json()
    assert 'kubernetes' in data
    assert 'monitoring' in data
    assert 'healing' in data
    assert 'alerts' in data
    assert 'dashboard' in data
