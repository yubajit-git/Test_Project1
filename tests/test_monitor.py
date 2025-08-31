"""
Tests for the monitoring functionality
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.monitor.cluster_monitor import ClusterMonitor
from src.database.models import NodeMetricsSchema, PodMetricsSchema


@pytest.fixture
def mock_k8s_client():
    """Mock Kubernetes client"""
    with patch('src.monitor.cluster_monitor.client') as mock_client:
        yield mock_client


@pytest.fixture
def cluster_monitor():
    """Create a cluster monitor instance"""
    with patch('src.monitor.cluster_monitor.config') as mock_config:
        mock_config.load_kube_config.side_effect = Exception("No kubeconfig")
        monitor = ClusterMonitor()
        return monitor


def test_cluster_monitor_initialization(cluster_monitor):
    """Test cluster monitor initialization"""
    assert cluster_monitor.monitoring_interval == 30
    assert not cluster_monitor.monitoring


def test_get_cluster_status_no_client(cluster_monitor):
    """Test cluster status when no client is available"""
    status = cluster_monitor.get_cluster_status()
    assert status['status'] == 'disconnected'
    assert 'Kubernetes client not available' in status['message']


@pytest.mark.asyncio
async def test_monitor_cycle_no_client(cluster_monitor):
    """Test monitoring cycle when no client is available"""
    await cluster_monitor._monitor_cycle()


def test_node_status_parsing():
    """Test node status parsing"""
    monitor = ClusterMonitor()
    
    mock_node = Mock()
    mock_node.status.conditions = [
        Mock(type='Ready', status='True'),
        Mock(type='MemoryPressure', status='False'),
        Mock(type='DiskPressure', status='False')
    ]
    mock_node.status.capacity = {'cpu': '4', 'memory': '8Gi'}
    
    status = monitor._get_node_status(mock_node)
    
    assert status['status'] == 'Ready'
    assert status['cpu_capacity'] == '4'
    assert status['memory_capacity'] == '8Gi'
    assert status['conditions']['Ready'] == 'True'


def test_pod_status_parsing():
    """Test pod status parsing"""
    monitor = ClusterMonitor()
    
    mock_pod = Mock()
    mock_pod.status.phase = 'Running'
    mock_pod.status.container_statuses = [
        Mock(restart_count=0, ready=True),
        Mock(restart_count=1, ready=True)
    ]
    
    status = monitor._get_pod_status(mock_pod)
    
    assert status['phase'] == 'Running'
    assert status['restart_count'] == 1
    assert status['ready'] is True
