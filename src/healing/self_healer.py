"""
Self-healing automation for Kubernetes resources
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from kubernetes import client
from kubernetes.client.rest import ApiException

from ..database.models import HealingActionSchema
from ..database.database import DatabaseManager
from ..config import config as app_config

logger = logging.getLogger(__name__)


class SelfHealer:
    """Self-healing automation service"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.healing = False
        self.healing_config = app_config.get_healing_config()
        self.enabled = self.healing_config.get('enabled', True)
        self.actions_config = self.healing_config.get('actions', {})
        self.thresholds = self.healing_config.get('thresholds', {})
        
        self.core_v1 = None
        self.apps_v1 = None
        
        if app_config.get('kubernetes'):
            try:
                self.core_v1 = client.CoreV1Api()
                self.apps_v1 = client.AppsV1Api()
            except Exception as e:
                logger.warning(f"Kubernetes client not available for healing: {e}")
    
    async def start_healing(self):
        """Start the self-healing loop"""
        if not self.enabled:
            logger.info("Self-healing is disabled")
            return
        
        self.healing = True
        logger.info("Starting self-healing service")
        
        while self.healing:
            try:
                await self._healing_cycle()
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in healing cycle: {e}")
                await asyncio.sleep(120)
    
    def stop_healing(self):
        """Stop the self-healing loop"""
        self.healing = False
        logger.info("Stopping self-healing service")
    
    async def _healing_cycle(self):
        """Single healing cycle"""
        logger.debug("Running healing cycle")
        
        if not self.core_v1:
            logger.debug("Kubernetes client not available, skipping healing")
            return
        
        await self._heal_failed_pods()
        await self._heal_pending_pods()
        await self._heal_deployments()
    
    async def _heal_failed_pods(self):
        """Restart failed pods"""
        if not self.actions_config.get('restart_failed_pods', True):
            return
        
        try:
            pods = self.core_v1.list_pod_for_all_namespaces()
            
            for pod in pods.items:
                if pod.status.phase == 'Failed':
                    await self._restart_pod(pod.metadata.name, pod.metadata.namespace, "Pod in Failed state")
                
                elif pod.status.container_statuses:
                    restart_threshold = self.thresholds.get('pod_restart_threshold', 5)
                    total_restarts = sum(cs.restart_count for cs in pod.status.container_statuses)
                    
                    if total_restarts >= restart_threshold:
                        await self._restart_pod(
                            pod.metadata.name, 
                            pod.metadata.namespace, 
                            f"Pod has {total_restarts} restarts (threshold: {restart_threshold})"
                        )
                        
        except ApiException as e:
            logger.error(f"Error healing failed pods: {e}")
        except Exception as e:
            logger.error(f"Unexpected error healing failed pods: {e}")
    
    async def _heal_pending_pods(self):
        """Handle pods stuck in pending state"""
        if not self.actions_config.get('reschedule_pending_pods', True):
            return
        
        try:
            pods = self.core_v1.list_pod_for_all_namespaces()
            pending_timeout = self.thresholds.get('pending_pod_timeout', 300)
            cutoff_time = datetime.utcnow() - timedelta(seconds=pending_timeout)
            
            for pod in pods.items:
                if pod.status.phase == 'Pending':
                    creation_time = pod.metadata.creation_timestamp.replace(tzinfo=None)
                    
                    if creation_time < cutoff_time:
                        await self._reschedule_pod(
                            pod.metadata.name, 
                            pod.metadata.namespace, 
                            f"Pod pending for more than {pending_timeout} seconds"
                        )
                        
        except ApiException as e:
            logger.error(f"Error healing pending pods: {e}")
        except Exception as e:
            logger.error(f"Unexpected error healing pending pods: {e}")
    
    async def _heal_deployments(self):
        """Scale deployments if needed"""
        if not self.actions_config.get('scale_deployments', True):
            return
        
        try:
            deployments = self.apps_v1.list_deployment_for_all_namespaces()
            
            for deployment in deployments.items:
                desired_replicas = deployment.spec.replicas or 0
                ready_replicas = deployment.status.ready_replicas or 0
                
                if desired_replicas > 0 and ready_replicas == 0:
                    await self._scale_deployment(
                        deployment.metadata.name,
                        deployment.metadata.namespace,
                        desired_replicas,
                        "No ready replicas available"
                    )
                        
        except ApiException as e:
            logger.error(f"Error healing deployments: {e}")
        except Exception as e:
            logger.error(f"Unexpected error healing deployments: {e}")
    
    async def _restart_pod(self, pod_name: str, namespace: str, reason: str):
        """Restart a pod by deleting it"""
        action = HealingActionSchema(
            action_type='restart_pod',
            resource_name=pod_name,
            namespace=namespace,
            reason=reason,
            status='PENDING',
            timestamp=datetime.utcnow()
        )
        
        action_id = await self.db_manager.store_healing_action(action)
        
        try:
            logger.info(f"Restarting pod {namespace}/{pod_name}: {reason}")
            
            self.core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )
            
            await self.db_manager.update_healing_action(
                action_id, 
                'SUCCESS', 
                f"Pod {namespace}/{pod_name} deleted for restart"
            )
            
        except ApiException as e:
            logger.error(f"Failed to restart pod {namespace}/{pod_name}: {e}")
            await self.db_manager.update_healing_action(
                action_id, 
                'FAILED', 
                f"API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error restarting pod {namespace}/{pod_name}: {e}")
            await self.db_manager.update_healing_action(
                action_id, 
                'FAILED', 
                f"Unexpected error: {e}"
            )
    
    async def _reschedule_pod(self, pod_name: str, namespace: str, reason: str):
        """Reschedule a pod by deleting and recreating it"""
        action = HealingActionSchema(
            action_type='reschedule_pod',
            resource_name=pod_name,
            namespace=namespace,
            reason=reason,
            status='PENDING',
            timestamp=datetime.utcnow()
        )
        
        action_id = await self.db_manager.store_healing_action(action)
        
        try:
            logger.info(f"Rescheduling pod {namespace}/{pod_name}: {reason}")
            
            self.core_v1.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace,
                body=client.V1DeleteOptions()
            )
            
            await self.db_manager.update_healing_action(
                action_id, 
                'SUCCESS', 
                f"Pod {namespace}/{pod_name} deleted for rescheduling"
            )
            
        except ApiException as e:
            logger.error(f"Failed to reschedule pod {namespace}/{pod_name}: {e}")
            await self.db_manager.update_healing_action(
                action_id, 
                'FAILED', 
                f"API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error rescheduling pod {namespace}/{pod_name}: {e}")
            await self.db_manager.update_healing_action(
                action_id, 
                'FAILED', 
                f"Unexpected error: {e}"
            )
    
    async def _scale_deployment(self, deployment_name: str, namespace: str, replicas: int, reason: str):
        """Scale a deployment"""
        action = HealingActionSchema(
            action_type='scale_deployment',
            resource_name=deployment_name,
            namespace=namespace,
            reason=reason,
            status='PENDING',
            timestamp=datetime.utcnow()
        )
        
        action_id = await self.db_manager.store_healing_action(action)
        
        try:
            logger.info(f"Scaling deployment {namespace}/{deployment_name} to {replicas} replicas: {reason}")
            
            body = {'spec': {'replicas': replicas}}
            self.apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body=body
            )
            
            await self.db_manager.update_healing_action(
                action_id, 
                'SUCCESS', 
                f"Deployment {namespace}/{deployment_name} scaled to {replicas} replicas"
            )
            
        except ApiException as e:
            logger.error(f"Failed to scale deployment {namespace}/{deployment_name}: {e}")
            await self.db_manager.update_healing_action(
                action_id, 
                'FAILED', 
                f"API error: {e}"
            )
        except Exception as e:
            logger.error(f"Unexpected error scaling deployment {namespace}/{deployment_name}: {e}")
            await self.db_manager.update_healing_action(
                action_id, 
                'FAILED', 
                f"Unexpected error: {e}"
            )
    
    def get_healing_status(self) -> Dict:
        """Get current healing status"""
        return {
            'enabled': self.enabled,
            'running': self.healing,
            'actions_enabled': self.actions_config,
            'thresholds': self.thresholds
        }
