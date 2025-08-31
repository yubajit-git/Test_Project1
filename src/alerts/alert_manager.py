"""
Alert and notification management
"""
import asyncio
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import requests

from ..database.models import AlertSchema
from ..database.database import DatabaseManager
from ..config import config as app_config

logger = logging.getLogger(__name__)


class AlertManager:
    """Alert and notification manager"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.alerts_config = app_config.get_alerts_config()
        self.enabled = self.alerts_config.get('enabled', True)
        self.channels = self.alerts_config.get('channels', [])
        
        self.alerting = False
    
    async def start_alerting(self):
        """Start the alerting service"""
        if not self.enabled:
            logger.info("Alerting is disabled")
            return
        
        self.alerting = True
        logger.info("Starting alerting service")
        
        while self.alerting:
            try:
                await self._process_alerts()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Error in alerting cycle: {e}")
                await asyncio.sleep(60)
    
    def stop_alerting(self):
        """Stop the alerting service"""
        self.alerting = False
        logger.info("Stopping alerting service")
    
    async def send_alert(self, alert_type: str, resource_name: str, namespace: str = "", 
                        message: str = "", severity: str = "INFO"):
        """Send an alert through configured channels"""
        if not self.enabled:
            return
        
        alert = AlertSchema(
            alert_type=alert_type,
            resource_name=resource_name,
            namespace=namespace,
            message=message,
            severity=severity,
            status='ACTIVE',
            channels_sent={},
            timestamp=datetime.utcnow()
        )
        
        channels_sent = {}
        
        for channel in self.channels:
            if not channel.get('enabled', True):
                continue
            
            channel_type = channel.get('type')
            try:
                if channel_type == 'log':
                    await self._send_log_alert(alert, channel)
                    channels_sent['log'] = 'SUCCESS'
                elif channel_type == 'webhook':
                    await self._send_webhook_alert(alert, channel)
                    channels_sent['webhook'] = 'SUCCESS'
                elif channel_type == 'email':
                    await self._send_email_alert(alert, channel)
                    channels_sent['email'] = 'SUCCESS'
                else:
                    logger.warning(f"Unknown alert channel type: {channel_type}")
                    
            except Exception as e:
                logger.error(f"Failed to send alert via {channel_type}: {e}")
                channels_sent[channel_type] = f'FAILED: {str(e)}'
        
        alert.channels_sent = channels_sent
        await self.db_manager.store_alert(alert)
    
    async def _send_log_alert(self, alert: AlertSchema, channel: Dict):
        """Send alert to log"""
        level = channel.get('level', 'INFO').upper()
        log_message = f"ALERT [{alert.severity}] {alert.alert_type}: {alert.resource_name}"
        if alert.namespace:
            log_message += f" (namespace: {alert.namespace})"
        if alert.message:
            log_message += f" - {alert.message}"
        
        if level == 'DEBUG':
            logger.debug(log_message)
        elif level == 'INFO':
            logger.info(log_message)
        elif level == 'WARNING':
            logger.warning(log_message)
        elif level == 'ERROR':
            logger.error(log_message)
        else:
            logger.info(log_message)
    
    async def _send_webhook_alert(self, alert: AlertSchema, channel: Dict):
        """Send alert via webhook"""
        url = channel.get('url')
        if not url:
            raise ValueError("Webhook URL not configured")
        
        payload = {
            'alert_type': alert.alert_type,
            'resource_name': alert.resource_name,
            'namespace': alert.namespace,
            'message': alert.message,
            'severity': alert.severity,
            'timestamp': alert.timestamp.isoformat()
        }
        
        headers = {'Content-Type': 'application/json'}
        timeout = channel.get('timeout', 10)
        
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
    
    async def _send_email_alert(self, alert: AlertSchema, channel: Dict):
        """Send alert via email"""
        smtp_server = channel.get('smtp_server')
        smtp_port = channel.get('smtp_port', 587)
        username = channel.get('username')
        password = channel.get('password')
        from_email = channel.get('from_email')
        to_emails = channel.get('to_emails', [])
        
        if not all([smtp_server, username, password, from_email, to_emails]):
            raise ValueError("Email configuration incomplete")
        
        subject = f"K8s Alert [{alert.severity}]: {alert.alert_type}"
        
        body = f"""
Kubernetes Health Monitoring Alert

Alert Type: {alert.alert_type}
Resource: {alert.resource_name}
Namespace: {alert.namespace or 'N/A'}
Severity: {alert.severity}
Timestamp: {alert.timestamp}

Message: {alert.message or 'No additional message'}

This alert was generated by the Kubernetes Health Monitoring System.
        """.strip()
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
    
    async def _process_alerts(self):
        """Process and manage active alerts"""
        pass
    
    async def send_node_alert(self, node_name: str, status: str, message: str = ""):
        """Send node-specific alert"""
        severity = 'ERROR' if status == 'NotReady' else 'WARNING'
        await self.send_alert(
            alert_type='node_unhealthy',
            resource_name=node_name,
            message=message or f"Node {node_name} is {status}",
            severity=severity
        )
    
    async def send_pod_alert(self, pod_name: str, namespace: str, status: str, message: str = ""):
        """Send pod-specific alert"""
        severity = 'ERROR' if status == 'Failed' else 'WARNING'
        await self.send_alert(
            alert_type='pod_unhealthy',
            resource_name=pod_name,
            namespace=namespace,
            message=message or f"Pod {namespace}/{pod_name} is {status}",
            severity=severity
        )
    
    async def send_deployment_alert(self, deployment_name: str, namespace: str, message: str = ""):
        """Send deployment-specific alert"""
        await self.send_alert(
            alert_type='deployment_unhealthy',
            resource_name=deployment_name,
            namespace=namespace,
            message=message,
            severity='WARNING'
        )
    
    async def send_healing_alert(self, action_type: str, resource_name: str, namespace: str, 
                                status: str, message: str = ""):
        """Send healing action alert"""
        severity = 'INFO' if status == 'SUCCESS' else 'ERROR'
        await self.send_alert(
            alert_type='healing_action',
            resource_name=resource_name,
            namespace=namespace,
            message=f"{action_type}: {message}",
            severity=severity
        )
    
    def get_alert_status(self) -> Dict:
        """Get current alert manager status"""
        return {
            'enabled': self.enabled,
            'running': self.alerting,
            'channels': [
                {
                    'type': channel.get('type'),
                    'enabled': channel.get('enabled', True)
                }
                for channel in self.channels
            ]
        }
