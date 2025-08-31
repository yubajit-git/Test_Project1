"""
API endpoints for the dashboard
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from ..database.database import DatabaseManager
from ..config import config

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")


manager = ConnectionManager()
db_manager = DatabaseManager()


def create_api_router() -> APIRouter:
    """Create API router with all endpoints"""
    router = APIRouter()
    
    @router.get("/status")
    async def get_system_status():
        """Get overall system status"""
        try:
            recent_nodes = db_manager.get_recent_node_metrics(hours=1)
            recent_pods = db_manager.get_recent_pod_metrics(hours=1)
            recent_events = db_manager.get_recent_events(hours=24)
            recent_actions = db_manager.get_recent_healing_actions(hours=24)
            active_alerts = db_manager.get_active_alerts()
            
            node_status = {}
            for node in recent_nodes:
                if node.node_name not in node_status or node.timestamp > node_status[node.node_name]['timestamp']:
                    node_status[node.node_name] = {
                        'status': node.status,
                        'timestamp': node.timestamp
                    }
            
            pod_status = {}
            for pod in recent_pods:
                key = f"{pod.namespace}/{pod.pod_name}"
                if key not in pod_status or pod.timestamp > pod_status[key]['timestamp']:
                    pod_status[key] = {
                        'status': pod.status,
                        'ready': pod.ready,
                        'restart_count': pod.restart_count,
                        'timestamp': pod.timestamp
                    }
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'nodes': {
                    'total': len(node_status),
                    'ready': sum(1 for n in node_status.values() if n['status'] == 'Ready'),
                    'details': node_status
                },
                'pods': {
                    'total': len(pod_status),
                    'running': sum(1 for p in pod_status.values() if p['status'] == 'Running' and p['ready']),
                    'details': pod_status
                },
                'events': {
                    'total': len(recent_events),
                    'last_24h': len(recent_events)
                },
                'healing_actions': {
                    'total': len(recent_actions),
                    'last_24h': len(recent_actions),
                    'successful': sum(1 for a in recent_actions if a.status == 'SUCCESS')
                },
                'alerts': {
                    'active': len(active_alerts)
                }
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/metrics/nodes")
    async def get_node_metrics(hours: int = 24):
        """Get node metrics"""
        try:
            metrics = db_manager.get_recent_node_metrics(hours=hours)
            return [
                {
                    'node_name': m.node_name,
                    'status': m.status,
                    'cpu_capacity': m.cpu_capacity,
                    'memory_capacity': m.memory_capacity,
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'conditions': m.conditions,
                    'timestamp': m.timestamp.isoformat()
                }
                for m in metrics
            ]
        except Exception as e:
            logger.error(f"Error getting node metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/metrics/pods")
    async def get_pod_metrics(hours: int = 24):
        """Get pod metrics"""
        try:
            metrics = db_manager.get_recent_pod_metrics(hours=hours)
            return [
                {
                    'pod_name': m.pod_name,
                    'namespace': m.namespace,
                    'status': m.status,
                    'restart_count': m.restart_count,
                    'ready': m.ready,
                    'node_name': m.node_name,
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'timestamp': m.timestamp.isoformat()
                }
                for m in metrics
            ]
        except Exception as e:
            logger.error(f"Error getting pod metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/events")
    async def get_cluster_events(hours: int = 24):
        """Get cluster events"""
        try:
            events = db_manager.get_recent_events(hours=hours)
            return [
                {
                    'id': e.id,
                    'event_type': e.event_type,
                    'resource_name': e.resource_name,
                    'namespace': e.namespace,
                    'message': e.message,
                    'severity': e.severity,
                    'timestamp': e.timestamp.isoformat()
                }
                for e in events
            ]
        except Exception as e:
            logger.error(f"Error getting cluster events: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/healing-actions")
    async def get_healing_actions(hours: int = 24):
        """Get healing actions"""
        try:
            actions = db_manager.get_recent_healing_actions(hours=hours)
            return [
                {
                    'id': a.id,
                    'action_type': a.action_type,
                    'resource_name': a.resource_name,
                    'namespace': a.namespace,
                    'reason': a.reason,
                    'status': a.status,
                    'result': a.result,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in actions
            ]
        except Exception as e:
            logger.error(f"Error getting healing actions: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/alerts")
    async def get_alerts():
        """Get active alerts"""
        try:
            alerts = db_manager.get_active_alerts()
            return [
                {
                    'id': a.id,
                    'alert_type': a.alert_type,
                    'resource_name': a.resource_name,
                    'namespace': a.namespace,
                    'message': a.message,
                    'severity': a.severity,
                    'status': a.status,
                    'channels_sent': a.channels_sent,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in alerts
            ]
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/config")
    async def get_configuration():
        """Get system configuration"""
        try:
            return {
                'kubernetes': config.get_kubernetes_config(),
                'monitoring': config.get_monitoring_config(),
                'healing': config.get_healing_config(),
                'alerts': config.get_alerts_config(),
                'dashboard': config.get_dashboard_config()
            }
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates"""
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
                
                status_data = await get_system_status()
                await websocket.send_json({
                    'type': 'status_update',
                    'data': status_data
                })
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)
    
    return router
