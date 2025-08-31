"""
Core cluster monitoring functionality
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from ..database.models import NodeMetricsSchema, PodMetricsSchema, ClusterEventSchema
from ..database.database import DatabaseManager
from ..config import config as app_config

logger = logging.getLogger(__name__)


class ClusterMonitor:
    """Main cluster monitoring class"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.k8s_client = None
        self.monitoring = False
        self.monitoring_interval = app_config.get('monitoring.interval', 30)
        self._load_k8s_config()
    
    def _load_k8s_config(self):
        """Load Kubernetes configuration"""
        k8s_config = app_config.get_kubernetes_config()
        
        try:
            if k8s_config.get('in_cluster', False):
                config.load_incluster_config()
                logger.info("Loaded in-cluster Kubernetes config")
            else:
                kubeconfig_path = k8s_config.get('kubeconfig_path', '~/.kube/config')
                config.load_kube_config(config_file=kubeconfig_path)
                logger.info("Loaded local Kubernetes config")
        except config.ConfigException as e:
            logger.warning(f"Failed to load Kubernetes config: {e}")
            logger.warning("Monitoring will run in mock mode")
            return
        
        self.k8s_client = client.ApiClient()
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.metrics_v1beta1 = client.CustomObjectsApi()
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        self.monitoring = True
        logger.info("Starting cluster monitoring")
        
        while self.monitoring:
            try:
                await self._monitor_cycle()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.monitoring = False
        logger.info("Stopping cluster monitoring")
    
    async def _monitor_cycle(self):
        """Single monitoring cycle"""
        logger.debug("Running monitoring cycle")
        
        if not self.k8s_client:
            logger.debug("Kubernetes client not available, skipping monitoring")
            return
        
        await self._monitor_nodes()
        await self._monitor_pods()
        await self._monitor_deployments()
    
    async def _monitor_nodes(self):
        """Monitor node health and status"""
        try:
            nodes = self.core_v1.list_node()
            
            for node in nodes.items:
                node_name = node.metadata.name
                node_status = self._get_node_status(node)
                
                metrics = NodeMetricsSchema(
                    node_name=node_name,
                    status=node_status['status'],
                    cpu_capacity=node_status['cpu_capacity'],
                    memory_capacity=node_status['memory_capacity'],
                    conditions=node_status['conditions'],
                    timestamp=datetime.utcnow()
                )
                
                await self.db_manager.store_node_metrics(metrics)
                
                if node_status['status'] != 'Ready':
                    await self._handle_unhealthy_node(node_name, node_status)
                    
        except ApiException as e:
            logger.error(f"Error monitoring nodes: {e}")
        except Exception as e:
            logger.error(f"Unexpected error monitoring nodes: {e}")
    
    async def _monitor_pods(self):
        """Monitor pod health and status"""
        try:
            namespace = app_config.get('kubernetes.namespace', '')
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace)
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
            
            for pod in pods.items:
                pod_name = pod.metadata.name
                namespace = pod.metadata.namespace
                pod_status = self._get_pod_status(pod)
                
                metrics = PodMetricsSchema(
                    pod_name=pod_name,
                    namespace=namespace,
                    status=pod_status['phase'],
                    restart_count=pod_status['restart_count'],
                    ready=pod_status['ready'],
                    node_name=pod.spec.node_name,
                    timestamp=datetime.utcnow()
                )
                
                await self.db_manager.store_pod_metrics(metrics)
                
                if pod_status['phase'] in ['Failed', 'Pending'] or not pod_status['ready']:
                    await self._handle_unhealthy_pod(pod_name, namespace, pod_status)
                    
        except ApiException as e:
            logger.error(f"Error monitoring pods: {e}")
        except Exception as e:
            logger.error(f"Unexpected error monitoring pods: {e}")
    
    async def _monitor_deployments(self):
        """Monitor deployment status"""
        try:
            namespace = app_config.get('kubernetes.namespace', '')
            if namespace:
                deployments = self.apps_v1.list_namespaced_deployment(namespace)
            else:
                deployments = self.apps_v1.list_deployment_for_all_namespaces()
            
            for deployment in deployments.items:
                deployment_name = deployment.metadata.name
                namespace = deployment.metadata.namespace
                
                replicas_desired = deployment.spec.replicas or 0
                replicas_ready = deployment.status.ready_replicas or 0
                replicas_available = deployment.status.available_replicas or 0
                
                if replicas_ready < replicas_desired:
                    await self._handle_unhealthy_deployment(deployment_name, namespace, {
                        'desired': replicas_desired,
                        'ready': replicas_ready,
                        'available': replicas_available
                    })
                    
        except ApiException as e:
            logger.error(f"Error monitoring deployments: {e}")
        except Exception as e:
            logger.error(f"Unexpected error monitoring deployments: {e}")
    
    def _get_node_status(self, node) -> Dict:
        """Extract node status information"""
        conditions = {}
        for condition in node.status.conditions or []:
            conditions[condition.type] = condition.status
        
        return {
            'status': 'Ready' if conditions.get('Ready') == 'True' else 'NotReady',
            'cpu_capacity': node.status.capacity.get('cpu', '0'),
            'memory_capacity': node.status.capacity.get('memory', '0'),
            'conditions': conditions
        }
    
    def _get_pod_status(self, pod) -> Dict:
        """Extract pod status information"""
        restart_count = 0
        ready = False
        
        if pod.status.container_statuses:
            restart_count = sum(cs.restart_count for cs in pod.status.container_statuses)
            ready = all(cs.ready for cs in pod.status.container_statuses)
        
        return {
            'phase': pod.status.phase,
            'restart_count': restart_count,
            'ready': ready
        }
    
    async def _handle_unhealthy_node(self, node_name: str, node_status: Dict):
        """Handle unhealthy node detection"""
        logger.warning(f"Unhealthy node detected: {node_name}")
        
        event = ClusterEventSchema(
            event_type='node_unhealthy',
            resource_name=node_name,
            namespace='',
            message=f"Node {node_name} is in {node_status['status']} state",
            severity='WARNING',
            timestamp=datetime.utcnow()
        )
        
        await self.db_manager.store_cluster_event(event)
    
    async def _handle_unhealthy_pod(self, pod_name: str, namespace: str, pod_status: Dict):
        """Handle unhealthy pod detection"""
        logger.warning(f"Unhealthy pod detected: {namespace}/{pod_name}")
        
        severity = 'ERROR' if pod_status['phase'] == 'Failed' else 'WARNING'
        
        event = ClusterEventSchema(
            event_type='pod_unhealthy',
            resource_name=pod_name,
            namespace=namespace,
            message=f"Pod {namespace}/{pod_name} is in {pod_status['phase']} state, ready: {pod_status['ready']}",
            severity=severity,
            timestamp=datetime.utcnow()
        )
        
        await self.db_manager.store_cluster_event(event)
    
    async def _handle_unhealthy_deployment(self, deployment_name: str, namespace: str, status: Dict):
        """Handle unhealthy deployment detection"""
        logger.warning(f"Unhealthy deployment detected: {namespace}/{deployment_name}")
        
        event = ClusterEventSchema(
            event_type='deployment_unhealthy',
            resource_name=deployment_name,
            namespace=namespace,
            message=f"Deployment {namespace}/{deployment_name} has {status['ready']}/{status['desired']} replicas ready",
            severity='WARNING',
            timestamp=datetime.utcnow()
        )
        
        await self.db_manager.store_cluster_event(event)
    
    def get_cluster_status(self) -> Dict:
        """Get current cluster status summary"""
        try:
            if not self.k8s_client:
                return {'status': 'disconnected', 'message': 'Kubernetes client not available'}
            
            nodes = self.core_v1.list_node()
            pods = self.core_v1.list_pod_for_all_namespaces()
            
            node_count = len(nodes.items)
            ready_nodes = sum(1 for node in nodes.items if self._get_node_status(node)['status'] == 'Ready')
            
            pod_count = len(pods.items)
            running_pods = sum(1 for pod in pods.items if pod.status.phase == 'Running')
            
            return {
                'status': 'connected',
                'nodes': {'total': node_count, 'ready': ready_nodes},
                'pods': {'total': pod_count, 'running': running_pods}
            }
        except Exception as e:
            logger.error(f"Error getting cluster status: {e}")
            return {'status': 'error', 'message': str(e)}
