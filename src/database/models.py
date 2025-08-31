"""
Database models for the Kubernetes Health Monitoring System
"""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()


class NodeMetrics(Base):
    """Node metrics table"""
    __tablename__ = "node_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    node_name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    cpu_capacity = Column(String(50))
    memory_capacity = Column(String(50))
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    conditions = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class PodMetrics(Base):
    """Pod metrics table"""
    __tablename__ = "pod_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    pod_name = Column(String(255), nullable=False, index=True)
    namespace = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    restart_count = Column(Integer, default=0)
    ready = Column(Boolean, default=False)
    node_name = Column(String(255))
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class DeploymentMetrics(Base):
    """Deployment metrics table"""
    __tablename__ = "deployment_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    deployment_name = Column(String(255), nullable=False, index=True)
    namespace = Column(String(255), nullable=False, index=True)
    replicas_desired = Column(Integer, default=0)
    replicas_ready = Column(Integer, default=0)
    replicas_available = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class ClusterEvent(Base):
    """Cluster events table"""
    __tablename__ = "cluster_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    resource_name = Column(String(255), nullable=False)
    namespace = Column(String(255), default="")
    message = Column(Text)
    severity = Column(String(20), default="INFO")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class HealingAction(Base):
    """Healing actions table"""
    __tablename__ = "healing_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    resource_name = Column(String(255), nullable=False)
    namespace = Column(String(255), default="")
    reason = Column(Text)
    status = Column(String(50), default="PENDING")
    result = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class Alert(Base):
    """Alerts table"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(100), nullable=False, index=True)
    resource_name = Column(String(255), nullable=False)
    namespace = Column(String(255), default="")
    message = Column(Text)
    severity = Column(String(20), default="INFO")
    status = Column(String(50), default="ACTIVE")
    channels_sent = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class NodeMetricsSchema(BaseModel):
    """Pydantic schema for node metrics"""
    node_name: str
    status: str
    cpu_capacity: Optional[str] = None
    memory_capacity: Optional[str] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    conditions: Optional[Dict[str, Any]] = None
    timestamp: datetime


class PodMetricsSchema(BaseModel):
    """Pydantic schema for pod metrics"""
    pod_name: str
    namespace: str
    status: str
    restart_count: int = 0
    ready: bool = False
    node_name: Optional[str] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    timestamp: datetime


class ClusterEventSchema(BaseModel):
    """Pydantic schema for cluster events"""
    event_type: str
    resource_name: str
    namespace: str = ""
    message: Optional[str] = None
    severity: str = "INFO"
    timestamp: datetime


class HealingActionSchema(BaseModel):
    """Pydantic schema for healing actions"""
    action_type: str
    resource_name: str
    namespace: str = ""
    reason: Optional[str] = None
    status: str = "PENDING"
    result: Optional[str] = None
    timestamp: datetime


class AlertSchema(BaseModel):
    """Pydantic schema for alerts"""
    alert_type: str
    resource_name: str
    namespace: str = ""
    message: Optional[str] = None
    severity: str = "INFO"
    status: str = "ACTIVE"
    channels_sent: Optional[Dict[str, Any]] = None
    timestamp: datetime
