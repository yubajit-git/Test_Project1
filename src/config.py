"""
Configuration management for the Kubernetes Health Monitoring System
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'kubernetes.namespace')"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_kubernetes_config(self) -> Dict[str, Any]:
        """Get Kubernetes configuration"""
        return self.get('kubernetes', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.get('monitoring', {})
    
    def get_healing_config(self) -> Dict[str, Any]:
        """Get self-healing configuration"""
        return self.get('healing', {})
    
    def get_alerts_config(self) -> Dict[str, Any]:
        """Get alerts configuration"""
        return self.get('alerts', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.get('database', {})
    
    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard configuration"""
        return self.get('dashboard', {})


config = Config()
