"""
Main entry point for the Kubernetes Health Monitoring System
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .monitor.cluster_monitor import ClusterMonitor
from .healing.self_healer import SelfHealer
from .alerts.alert_manager import AlertManager
from .dashboard.api import create_api_router
from .config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Kubernetes Health Monitoring System")
    
    monitor = ClusterMonitor()
    healer = SelfHealer()
    alert_manager = AlertManager()
    
    monitor_task = asyncio.create_task(monitor.start_monitoring())
    healer_task = asyncio.create_task(healer.start_healing())
    alert_task = asyncio.create_task(alert_manager.start_alerting())
    
    app.state.monitor = monitor
    app.state.healer = healer
    app.state.alert_manager = alert_manager
    
    yield
    
    logger.info("Shutting down Kubernetes Health Monitoring System")
    monitor.stop_monitoring()
    healer.stop_healing()
    alert_manager.stop_alerting()
    
    monitor_task.cancel()
    healer_task.cancel()
    alert_task.cancel()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Kubernetes Health Monitoring System",
        description="Automated health monitoring with self-healing capabilities",
        version="1.0.0",
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    api_router = create_api_router()
    app.include_router(api_router, prefix="/api")
    
    @app.get("/")
    async def root():
        return {"message": "Kubernetes Health Monitoring System", "status": "running"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    dashboard_config = config.get_dashboard_config()
    host = dashboard_config.get('host', '0.0.0.0')
    port = dashboard_config.get('port', 8000)
    
    uvicorn.run(app, host=host, port=port)
