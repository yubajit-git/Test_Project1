"""
Database management for the Kubernetes Health Monitoring System
"""
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, NodeMetrics, PodMetrics, DeploymentMetrics, ClusterEvent, HealingAction, Alert
from .models import NodeMetricsSchema, PodMetricsSchema, ClusterEventSchema, HealingActionSchema, AlertSchema
from ..config import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for the monitoring system"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables"""
        db_config = config.get_database_config()
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            db_path = db_config.get('sqlite', {}).get('path', 'data/monitoring.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            database_url = f"sqlite:///{db_path}"
        elif db_type == 'postgresql':
            pg_config = db_config.get('postgresql', {})
            host = pg_config.get('host', 'localhost')
            port = pg_config.get('port', 5432)
            database = pg_config.get('database', 'k8s_monitoring')
            username = pg_config.get('username', 'postgres')
            password = pg_config.get('password', '')
            database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized with {db_type}")
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    async def store_node_metrics(self, metrics: NodeMetricsSchema):
        """Store node metrics"""
        try:
            with self.get_session() as session:
                db_metrics = NodeMetrics(
                    node_name=metrics.node_name,
                    status=metrics.status,
                    cpu_capacity=metrics.cpu_capacity,
                    memory_capacity=metrics.memory_capacity,
                    cpu_usage=metrics.cpu_usage,
                    memory_usage=metrics.memory_usage,
                    conditions=metrics.conditions,
                    timestamp=metrics.timestamp
                )
                session.add(db_metrics)
                session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error storing node metrics: {e}")
    
    async def store_pod_metrics(self, metrics: PodMetricsSchema):
        """Store pod metrics"""
        try:
            with self.get_session() as session:
                db_metrics = PodMetrics(
                    pod_name=metrics.pod_name,
                    namespace=metrics.namespace,
                    status=metrics.status,
                    restart_count=metrics.restart_count,
                    ready=metrics.ready,
                    node_name=metrics.node_name,
                    cpu_usage=metrics.cpu_usage,
                    memory_usage=metrics.memory_usage,
                    timestamp=metrics.timestamp
                )
                session.add(db_metrics)
                session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error storing pod metrics: {e}")
    
    async def store_cluster_event(self, event: ClusterEventSchema):
        """Store cluster event"""
        try:
            with self.get_session() as session:
                db_event = ClusterEvent(
                    event_type=event.event_type,
                    resource_name=event.resource_name,
                    namespace=event.namespace,
                    message=event.message,
                    severity=event.severity,
                    timestamp=event.timestamp
                )
                session.add(db_event)
                session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error storing cluster event: {e}")
    
    async def store_healing_action(self, action: HealingActionSchema):
        """Store healing action"""
        try:
            with self.get_session() as session:
                db_action = HealingAction(
                    action_type=action.action_type,
                    resource_name=action.resource_name,
                    namespace=action.namespace,
                    reason=action.reason,
                    status=action.status,
                    result=action.result,
                    timestamp=action.timestamp
                )
                session.add(db_action)
                session.commit()
                return db_action.id
        except SQLAlchemyError as e:
            logger.error(f"Error storing healing action: {e}")
            return None
    
    async def update_healing_action(self, action_id: int, status: str, result: str):
        """Update healing action status"""
        try:
            with self.get_session() as session:
                action = session.query(HealingAction).filter(HealingAction.id == action_id).first()
                if action:
                    action.status = status
                    action.result = result
                    session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error updating healing action: {e}")
    
    async def store_alert(self, alert: AlertSchema):
        """Store alert"""
        try:
            with self.get_session() as session:
                db_alert = Alert(
                    alert_type=alert.alert_type,
                    resource_name=alert.resource_name,
                    namespace=alert.namespace,
                    message=alert.message,
                    severity=alert.severity,
                    status=alert.status,
                    channels_sent=alert.channels_sent,
                    timestamp=alert.timestamp
                )
                session.add(db_alert)
                session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error storing alert: {e}")
    
    def get_recent_node_metrics(self, hours: int = 24) -> List[NodeMetrics]:
        """Get recent node metrics"""
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                return session.query(NodeMetrics).filter(
                    NodeMetrics.timestamp >= cutoff_time
                ).order_by(desc(NodeMetrics.timestamp)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting node metrics: {e}")
            return []
    
    def get_recent_pod_metrics(self, hours: int = 24) -> List[PodMetrics]:
        """Get recent pod metrics"""
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                return session.query(PodMetrics).filter(
                    PodMetrics.timestamp >= cutoff_time
                ).order_by(desc(PodMetrics.timestamp)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting pod metrics: {e}")
            return []
    
    def get_recent_events(self, hours: int = 24) -> List[ClusterEvent]:
        """Get recent cluster events"""
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                return session.query(ClusterEvent).filter(
                    ClusterEvent.timestamp >= cutoff_time
                ).order_by(desc(ClusterEvent.timestamp)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cluster events: {e}")
            return []
    
    def get_recent_healing_actions(self, hours: int = 24) -> List[HealingAction]:
        """Get recent healing actions"""
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                return session.query(HealingAction).filter(
                    HealingAction.timestamp >= cutoff_time
                ).order_by(desc(HealingAction.timestamp)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting healing actions: {e}")
            return []
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        try:
            with self.get_session() as session:
                return session.query(Alert).filter(
                    Alert.status == "ACTIVE"
                ).order_by(desc(Alert.timestamp)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data"""
        try:
            with self.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(days=days)
                
                session.query(NodeMetrics).filter(NodeMetrics.timestamp < cutoff_time).delete()
                session.query(PodMetrics).filter(PodMetrics.timestamp < cutoff_time).delete()
                session.query(ClusterEvent).filter(ClusterEvent.timestamp < cutoff_time).delete()
                session.query(HealingAction).filter(HealingAction.timestamp < cutoff_time).delete()
                session.query(Alert).filter(Alert.timestamp < cutoff_time).delete()
                
                session.commit()
                logger.info(f"Cleaned up data older than {days} days")
        except SQLAlchemyError as e:
            logger.error(f"Error cleaning up old data: {e}")
