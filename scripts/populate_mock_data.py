#!/usr/bin/env python3
"""
Script to populate mock data for demonstration purposes
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import DatabaseManager
from src.database.models import NodeMetricsSchema, PodMetricsSchema, ClusterEventSchema, HealingActionSchema

async def populate_mock_data():
    """Populate database with mock data for demonstration"""
    db_manager = DatabaseManager()
    
    nodes = [
        {"name": "worker-node-1", "status": "Ready", "cpu": "4", "memory": "8Gi"},
        {"name": "worker-node-2", "status": "Ready", "cpu": "4", "memory": "8Gi"},
        {"name": "master-node-1", "status": "Ready", "cpu": "2", "memory": "4Gi"},
    ]
    
    pods = [
        {"name": "nginx-deployment-abc123", "namespace": "default", "status": "Running", "restarts": 0, "ready": True, "node": "worker-node-1"},
        {"name": "redis-cache-def456", "namespace": "default", "status": "Running", "restarts": 1, "ready": True, "node": "worker-node-2"},
        {"name": "api-server-ghi789", "namespace": "kube-system", "status": "Running", "restarts": 0, "ready": True, "node": "master-node-1"},
        {"name": "failing-pod-jkl012", "namespace": "default", "status": "Failed", "restarts": 3, "ready": False, "node": "worker-node-1"},
        {"name": "pending-pod-mno345", "namespace": "default", "status": "Pending", "restarts": 0, "ready": False, "node": None},
    ]
    
    base_time = datetime.utcnow()
    
    for i in range(12):  # 12 data points over last hour (5 min intervals)
        timestamp = base_time - timedelta(minutes=i * 5)
        
        for node in nodes:
            node_metrics = NodeMetricsSchema(
                node_name=node["name"],
                status=node["status"],
                cpu_capacity=node["cpu"],
                memory_capacity=node["memory"],
                conditions={"Ready": "True", "MemoryPressure": "False", "DiskPressure": "False"},
                timestamp=timestamp
            )
            await db_manager.store_node_metrics(node_metrics)
        
        for pod in pods:
            pod_metrics = PodMetricsSchema(
                pod_name=pod["name"],
                namespace=pod["namespace"],
                status=pod["status"],
                restart_count=pod["restarts"] + random.randint(0, 1) if i < 6 else pod["restarts"],
                ready=pod["ready"],
                node_name=pod["node"],
                timestamp=timestamp
            )
            await db_manager.store_pod_metrics(pod_metrics)
    
    events = [
        {"type": "pod_unhealthy", "resource": "failing-pod-jkl012", "namespace": "default", "message": "Pod failed to start", "severity": "ERROR"},
        {"type": "node_ready", "resource": "worker-node-1", "namespace": "", "message": "Node is ready", "severity": "INFO"},
        {"type": "pod_restart", "resource": "redis-cache-def456", "namespace": "default", "message": "Pod restarted due to failure", "severity": "WARNING"},
    ]
    
    for i, event in enumerate(events):
        event_time = base_time - timedelta(minutes=i * 10)
        cluster_event = ClusterEventSchema(
            event_type=event["type"],
            resource_name=event["resource"],
            namespace=event["namespace"],
            message=event["message"],
            severity=event["severity"],
            timestamp=event_time
        )
        await db_manager.store_cluster_event(cluster_event)
    
    healing_actions = [
        {"type": "restart_pod", "resource": "failing-pod-jkl012", "namespace": "default", "status": "success", "message": "Pod restarted successfully"},
        {"type": "reschedule_pod", "resource": "pending-pod-mno345", "namespace": "default", "status": "failed", "message": "Failed to reschedule pod"},
        {"type": "scale_deployment", "resource": "nginx-deployment", "namespace": "default", "status": "success", "message": "Scaled deployment to 3 replicas"},
    ]
    
    for i, action in enumerate(healing_actions):
        action_time = base_time - timedelta(minutes=i * 15)
        healing_action = HealingActionSchema(
            action_type=action["type"],
            resource_name=action["resource"],
            namespace=action["namespace"],
            status=action["status"],
            message=action["message"],
            timestamp=action_time
        )
        await db_manager.store_healing_action(healing_action)
    
    print("Mock data populated successfully!")

if __name__ == "__main__":
    asyncio.run(populate_mock_data())
