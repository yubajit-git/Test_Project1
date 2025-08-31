"""
Tests for the alerting functionality
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.alerts.alert_manager import AlertManager


@pytest.fixture
def alert_manager():
    """Create an alert manager instance"""
    with patch('src.alerts.alert_manager.app_config') as mock_config:
        mock_config.get_alerts_config.return_value = {
            'enabled': True,
            'channels': [
                {'type': 'log', 'level': 'INFO'},
                {'type': 'webhook', 'url': 'http://test.com/webhook', 'enabled': False}
            ]
        }
        manager = AlertManager()
        return manager


def test_alert_manager_initialization(alert_manager):
    """Test alert manager initialization"""
    assert alert_manager.enabled is True
    assert len(alert_manager.channels) == 2


@pytest.mark.asyncio
async def test_send_log_alert(alert_manager):
    """Test sending log alert"""
    alert_manager.db_manager = Mock()
    alert_manager.db_manager.store_alert = AsyncMock()
    
    with patch('src.alerts.alert_manager.logger') as mock_logger:
        await alert_manager.send_alert(
            alert_type='test_alert',
            resource_name='test-resource',
            message='Test message',
            severity='INFO'
        )
        
        mock_logger.info.assert_called()
        alert_manager.db_manager.store_alert.assert_called_once()


def test_alert_status(alert_manager):
    """Test getting alert manager status"""
    status = alert_manager.get_alert_status()
    
    assert status['enabled'] is True
    assert status['running'] is False
    assert len(status['channels']) == 2
