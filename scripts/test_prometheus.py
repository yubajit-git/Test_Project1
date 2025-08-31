#!/usr/bin/env python3
"""
Script to test PrometheusExporter functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.metrics.prometheus_exporter import PrometheusExporter

def test_prometheus_exporter():
    print("Testing PrometheusExporter...")
    
    exporter = PrometheusExporter()
    print("PrometheusExporter initialized successfully")
    
    try:
        exporter.update_metrics()
        print("Metrics updated successfully")
    except Exception as e:
        print(f"Error updating metrics: {e}")
        import traceback
        traceback.print_exc()
        return
    
    metrics_output = exporter.get_metrics()
    print(f"Generated metrics (first 500 chars):")
    print(metrics_output[:500])
    print("...")
    
    if "k8s_node_status{" in metrics_output:
        print("✓ Node status metrics found")
    else:
        print("✗ Node status metrics NOT found")
    
    if "k8s_pod_status{" in metrics_output:
        print("✓ Pod status metrics found")
    else:
        print("✗ Pod status metrics NOT found")
    
    if "k8s_monitoring_cycles_total" in metrics_output:
        print("✓ Monitoring cycles metric found")
    else:
        print("✗ Monitoring cycles metric NOT found")

if __name__ == "__main__":
    test_prometheus_exporter()
