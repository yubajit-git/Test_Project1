#!/usr/bin/env python3
"""
Script to check database contents
"""
import sqlite3
import os

db_path = "data/monitoring.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM node_metrics')
    node_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM pod_metrics') 
    pod_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM cluster_events')
    event_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM healing_actions')
    healing_count = cursor.fetchone()[0]
    
    print(f'Database contents:')
    print(f'  Node metrics: {node_count}')
    print(f'  Pod metrics: {pod_count}')
    print(f'  Cluster events: {event_count}')
    print(f'  Healing actions: {healing_count}')
    
    cursor.execute('SELECT node_name, status FROM node_metrics LIMIT 3')
    nodes = cursor.fetchall()
    print(f'  Sample nodes: {nodes}')
    
    conn.close()
else:
    print(f"Database not found at {db_path}")
