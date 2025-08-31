"""
Prometheus metrics exporter for Kubernetes cluster monitoring
"""
import logging
from typing import Dict, List
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest
from prometheus_client.core import REGISTRY
from datetime import datetime, timedelta
from sqlalchemy import text

from ..database.database import DatabaseManager
from ..config import config as app_config

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """Exports cluster monitoring metrics to Prometheus format"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.registry = CollectorRegistry()
        self._init_metrics()
    
    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        self.node_status = Gauge(
            'k8s_node_status',
            'Node status (1=Ready, 0=NotReady)',
            ['node_name'],
            registry=self.registry
        )
        
        self.node_cpu_capacity = Gauge(
            'k8s_node_cpu_capacity_cores',
            'Node CPU capacity in cores',
            ['node_name'],
            registry=self.registry
        )
        
        self.node_memory_capacity = Gauge(
            'k8s_node_memory_capacity_bytes',
            'Node memory capacity in bytes',
            ['node_name'],
            registry=self.registry
        )
        
        self.pod_status = Gauge(
            'k8s_pod_status',
            'Pod status (1=Running, 0=Other)',
            ['pod_name', 'namespace', 'node_name'],
            registry=self.registry
        )
        
        self.pod_restart_count = Counter(
            'k8s_pod_restart_count_total',
            'Total pod restart count',
            ['pod_name', 'namespace'],
            registry=self.registry
        )
        
        self.pod_ready = Gauge(
            'k8s_pod_ready',
            'Pod ready status (1=Ready, 0=NotReady)',
            ['pod_name', 'namespace'],
            registry=self.registry
        )
        
        self.cluster_events_total = Counter(
            'k8s_cluster_events_total',
            'Total cluster events',
            ['event_type', 'severity'],
            registry=self.registry
        )
        
        self.healing_actions_total = Counter(
            'k8s_healing_actions_total',
            'Total healing actions performed',
            ['action_type', 'status'],
            registry=self.registry
        )
        
        self.monitoring_cycles_total = Counter(
            'k8s_monitoring_cycles_total',
            'Total monitoring cycles completed',
            registry=self.registry
        )
        
        self.monitoring_cycle_duration = Histogram(
            'k8s_monitoring_cycle_duration_seconds',
            'Duration of monitoring cycles',
            registry=self.registry
        )
    
    def update_metrics(self):
        """Update all Prometheus metrics from database"""
        try:
            self._update_node_metrics()
            self._update_pod_metrics()
            self._update_event_metrics()
            self._update_healing_metrics()
            logger.debug("Updated Prometheus metrics")
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
    
    def _update_node_metrics(self):
        """Update node-related metrics"""
        query = """
        SELECT node_name, status, cpu_capacity, memory_capacity, timestamp
        FROM node_metrics 
        WHERE (node_name, timestamp) IN (
            SELECT node_name, MAX(timestamp)
            FROM node_metrics
            GROUP BY node_name
        )
        ORDER BY node_name
        """
        
        with self.db_manager.get_session() as session:
            result = session.execute(text(query))
            nodes = result.fetchall()
            
            for node in nodes:
                node_name = node.node_name
                
                status_value = 1 if node.status == 'Ready' else 0
                self.node_status.labels(node_name=node_name).set(status_value)
                
                try:
                    cpu_cores = float(node.cpu_capacity.rstrip('m')) / 1000 if 'm' in node.cpu_capacity else float(node.cpu_capacity)
                    self.node_cpu_capacity.labels(node_name=node_name).set(cpu_cores)
                except (ValueError, AttributeError):
                    logger.warning(f"Could not parse CPU capacity for node {node_name}: {node.cpu_capacity}")
                
                try:
                    memory_str = node.memory_capacity
                    if 'Ki' in memory_str:
                        memory_bytes = float(memory_str.replace('Ki', '')) * 1024
                    elif 'Mi' in memory_str:
                        memory_bytes = float(memory_str.replace('Mi', '')) * 1024 * 1024
                    elif 'Gi' in memory_str:
                        memory_bytes = float(memory_str.replace('Gi', '')) * 1024 * 1024 * 1024
                    else:
                        memory_bytes = float(memory_str)
                    
                    self.node_memory_capacity.labels(node_name=node_name).set(memory_bytes)
                except (ValueError, AttributeError):
                    logger.warning(f"Could not parse memory capacity for node {node_name}: {node.memory_capacity}")
    
    def _update_pod_metrics(self):
        """Update pod-related metrics"""
        query = """
        SELECT pod_name, namespace, status, restart_count, ready, node_name, timestamp
        FROM pod_metrics 
        WHERE (pod_name, namespace, timestamp) IN (
            SELECT pod_name, namespace, MAX(timestamp)
            FROM pod_metrics
            GROUP BY pod_name, namespace
        )
        ORDER BY pod_name, namespace
        """
        
        with self.db_manager.get_session() as session:
            result = session.execute(text(query))
            pods = result.fetchall()
            
            for pod in pods:
                pod_name = pod.pod_name
                namespace = pod.namespace
                node_name = pod.node_name or 'unknown'
                
                status_value = 1 if pod.status == 'Running' else 0
                self.pod_status.labels(
                    pod_name=pod_name,
                    namespace=namespace,
                    node_name=node_name
                ).set(status_value)
                
                ready_value = 1 if pod.ready else 0
                self.pod_ready.labels(
                    pod_name=pod_name,
                    namespace=namespace
                ).set(ready_value)
                
                self.pod_restart_count.labels(
                    pod_name=pod_name,
                    namespace=namespace
                )._value._value = pod.restart_count
    
    def _update_event_metrics(self):
        """Update cluster event metrics"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        query = """
        SELECT event_type, severity, COUNT(*) as count
        FROM cluster_events 
        WHERE timestamp > :timestamp
        GROUP BY event_type, severity
        """
        
        with self.db_manager.get_session() as session:
            result = session.execute(text(query), {"timestamp": one_hour_ago})
            events = result.fetchall()
            
            for event in events:
                self.cluster_events_total.labels(
                    event_type=event.event_type,
                    severity=event.severity
                )._value._value = event.count
    
    def _update_healing_metrics(self):
        """Update healing action metrics"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        query = """
        SELECT action_type, status, COUNT(*) as count
        FROM healing_actions 
        WHERE timestamp > :timestamp
        GROUP BY action_type, status
        """
        
        with self.db_manager.get_session() as session:
            result = session.execute(text(query), {"timestamp": one_hour_ago})
            actions = result.fetchall()
            
            for action in actions:
                self.healing_actions_total.labels(
                    action_type=action.action_type,
                    status=action.status
                )._value._value = action.count
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')
    
    def record_monitoring_cycle(self, duration: float):
        """Record a completed monitoring cycle"""
        self.monitoring_cycles_total.inc()
        self.monitoring_cycle_duration.observe(duration)
