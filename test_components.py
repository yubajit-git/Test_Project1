#!/usr/bin/env python3
"""
Test script to verify all system components work correctly
"""
import sys
import os
sys.path.append('.')

from src.config import config
from src.database.database import DatabaseManager
from src.monitor.cluster_monitor import ClusterMonitor
from src.healing.self_healer import SelfHealer
from src.alerts.alert_manager import AlertManager

def test_components():
    print('Testing configuration loading...')
    k8s_config = config.get_kubernetes_config()
    print(f'Kubernetes config: {k8s_config}')

    print('\nTesting database initialization...')
    db = DatabaseManager()
    print('Database initialized successfully')

    print('\nTesting cluster monitor...')
    monitor = ClusterMonitor()
    status = monitor.get_cluster_status()
    print(f'Cluster status: {status}')

    print('\nTesting self healer...')
    healer = SelfHealer()
    healing_status = healer.get_healing_status()
    print(f'Healing status: {healing_status}')

    print('\nTesting alert manager...')
    alert_mgr = AlertManager()
    alert_status = alert_mgr.get_alert_status()
    print(f'Alert status: {alert_status}')

    print('\nAll components initialized successfully!')
    return True

if __name__ == '__main__':
    test_components()
