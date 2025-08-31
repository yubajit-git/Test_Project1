"""
Slack notification integration for alerts
"""
import logging
import json
import aiohttp
from typing import Dict, Any, Optional
from ..config import config

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Slack notification service for alerts"""
    
    def __init__(self):
        self.webhook_url = config.get_alert_config().get('slack', {}).get('webhook_url')
        self.channel = config.get_alert_config().get('slack', {}).get('channel', '#alerts')
        self.username = config.get_alert_config().get('slack', {}).get('username', 'K8s Health Monitor')
        self.enabled = bool(self.webhook_url)
        
        if not self.enabled:
            logger.warning("Slack webhook URL not configured, Slack notifications disabled")
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send alert to Slack channel"""
        if not self.enabled:
            logger.debug("Slack notifications disabled, skipping alert")
            return False
        
        try:
            message = self._format_alert_message(alert_data)
            payload = {
                "channel": self.channel,
                "username": self.username,
                "text": message,
                "attachments": [self._create_attachment(alert_data)]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack alert sent successfully for {alert_data.get('resource_name')}")
                        return True
                    else:
                        logger.error(f"Failed to send Slack alert: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False
    
    def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Format alert message for Slack"""
        severity = alert_data.get('severity', 'INFO')
        alert_type = alert_data.get('alert_type', 'Unknown')
        resource_name = alert_data.get('resource_name', 'Unknown')
        namespace = alert_data.get('namespace', '')
        
        emoji = self._get_severity_emoji(severity)
        namespace_text = f" in namespace `{namespace}`" if namespace else ""
        
        return f"{emoji} *{severity}* - {alert_type} for `{resource_name}`{namespace_text}"
    
    def _create_attachment(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Slack attachment with alert details"""
        severity = alert_data.get('severity', 'INFO')
        color = self._get_severity_color(severity)
        
        fields = [
            {
                "title": "Resource",
                "value": alert_data.get('resource_name', 'Unknown'),
                "short": True
            },
            {
                "title": "Alert Type",
                "value": alert_data.get('alert_type', 'Unknown'),
                "short": True
            }
        ]
        
        if alert_data.get('namespace'):
            fields.append({
                "title": "Namespace",
                "value": alert_data.get('namespace'),
                "short": True
            })
        
        if alert_data.get('message'):
            fields.append({
                "title": "Details",
                "value": alert_data.get('message'),
                "short": False
            })
        
        return {
            "color": color,
            "fields": fields,
            "footer": "K8s Health Monitor",
            "ts": int(alert_data.get('timestamp', 0))
        }
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji for alert severity"""
        emoji_map = {
            'ERROR': '🚨',
            'WARNING': '⚠️',
            'INFO': 'ℹ️',
            'DEBUG': '🔍'
        }
        return emoji_map.get(severity.upper(), 'ℹ️')
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for alert severity"""
        color_map = {
            'ERROR': 'danger',
            'WARNING': 'warning',
            'INFO': 'good',
            'DEBUG': '#36a64f'
        }
        return color_map.get(severity.upper(), 'good')
    
    async def send_healing_action_notification(self, action_data: Dict[str, Any]) -> bool:
        """Send healing action notification to Slack"""
        if not self.enabled:
            return False
        
        try:
            status = action_data.get('status', 'UNKNOWN')
            action_type = action_data.get('action_type', 'Unknown')
            resource_name = action_data.get('resource_name', 'Unknown')
            namespace = action_data.get('namespace', '')
            
            emoji = '✅' if status == 'SUCCESS' else '❌' if status == 'FAILED' else '⏳'
            namespace_text = f" in namespace `{namespace}`" if namespace else ""
            
            message = f"{emoji} Healing action *{action_type}* for `{resource_name}`{namespace_text} - Status: *{status}*"
            
            payload = {
                "channel": self.channel,
                "username": self.username,
                "text": message,
                "attachments": [{
                    "color": "good" if status == 'SUCCESS' else "danger" if status == 'FAILED' else "warning",
                    "fields": [
                        {
                            "title": "Action Type",
                            "value": action_type,
                            "short": True
                        },
                        {
                            "title": "Resource",
                            "value": resource_name,
                            "short": True
                        },
                        {
                            "title": "Status",
                            "value": status,
                            "short": True
                        }
                    ] + ([{
                        "title": "Namespace",
                        "value": namespace,
                        "short": True
                    }] if namespace else []) + ([{
                        "title": "Reason",
                        "value": action_data.get('reason', ''),
                        "short": False
                    }] if action_data.get('reason') else []),
                    "footer": "K8s Health Monitor - Healing Actions",
                    "ts": int(action_data.get('timestamp', 0))
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack healing action notification sent for {resource_name}")
                        return True
                    else:
                        logger.error(f"Failed to send Slack healing notification: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Slack healing notification: {e}")
            return False
