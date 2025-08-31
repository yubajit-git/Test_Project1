export interface SystemStatus {
  timestamp: string
  nodes: {
    total: number
    ready: number
    details: Record<string, {
      status: string
      timestamp: string
    }>
  }
  pods: {
    total: number
    running: number
    details: Record<string, {
      status: string
      ready: boolean
      restart_count: number
      timestamp: string
    }>
  }
  events: {
    total: number
    last_24h: number
  }
  healing_actions: {
    total: number
    last_24h: number
    successful: number
  }
  alerts: {
    active: number
  }
}

export interface NodeMetric {
  node_name: string
  status: string
  cpu_capacity: string
  memory_capacity: string
  cpu_usage: number
  memory_usage: number
  conditions: Record<string, string>
  timestamp: string
}

export interface PodMetric {
  pod_name: string
  namespace: string
  status: string
  restart_count: number
  ready: boolean
  node_name: string
  cpu_usage: number
  memory_usage: number
  timestamp: string
}

export interface ClusterEvent {
  id: number
  event_type: string
  resource_name: string
  namespace: string
  message: string
  severity: string
  timestamp: string
}

export interface HealingAction {
  id: number
  action_type: string
  resource_name: string
  namespace: string
  reason: string
  status: string
  result: string
  timestamp: string
}

export interface Alert {
  id: number
  alert_type: string
  resource_name: string
  namespace: string
  message: string
  severity: string
  status: string
  channels_sent: Record<string, string>
  timestamp: string
}
