"""
Tests for the self-healing functionality
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.healing.self_healer import SelfHealer


@pytest.fixture
def self_healer():
    """Create a self healer instance"""
    with patch('src.healing.self_healer.app_config') as mock_config:
        mock_config.get_healing_config.return_value = {
            'enabled': True,
            'actions': {
                'restart_failed_pods': True,
                'reschedule_pending_pods': True,
                'scale_deployments': True
            },
            'thresholds': {
                'pod_restart_threshold': 5,
                'pending_pod_timeout': 300,
                'cpu_threshold': 80,
                'memory_threshold': 80
            }
        }
        healer = SelfHealer()
        return healer


def test_self_healer_initialization(self_healer):
    """Test self healer initialization"""
    assert self_healer.enabled is True
    assert self_healer.actions_config['restart_failed_pods'] is True
    assert self_healer.thresholds['pod_restart_threshold'] == 5


def test_healing_status(self_healer):
    """Test getting healing status"""
    status = self_healer.get_healing_status()
    
    assert status['enabled'] is True
    assert status['running'] is False
    assert 'actions_enabled' in status
    assert 'thresholds' in status


@pytest.mark.asyncio
async def test_healing_cycle_no_client(self_healer):
    """Test healing cycle when no client is available"""
    await self_healer._healing_cycle()


@pytest.mark.asyncio
async def test_restart_pod(self_healer):
    """Test pod restart functionality"""
    self_healer.core_v1 = Mock()
    self_healer.db_manager = Mock()
    self_healer.db_manager.store_healing_action = AsyncMock(return_value=1)
    self_healer.db_manager.update_healing_action = AsyncMock()
    
    await self_healer._restart_pod('test-pod', 'default', 'Pod in Failed state')
    
    self_healer.core_v1.delete_namespaced_pod.assert_called_once()
    self_healer.db_manager.store_healing_action.assert_called_once()
    self_healer.db_manager.update_healing_action.assert_called_once()
