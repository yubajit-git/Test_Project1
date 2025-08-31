import React, { useEffect, useState } from 'react'
import { Server, Package, AlertTriangle, Wrench, Activity } from 'lucide-react'
import { SystemStatus, ClusterEvent, HealingAction } from '../types'

const Card = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
  <div className={`bg-white shadow rounded-lg ${className}`}>{children}</div>
)

const CardHeader = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
  <div className={`px-6 py-4 border-b border-gray-200 ${className}`}>{children}</div>
)

const CardTitle = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
  <h3 className={`text-lg font-medium text-gray-900 ${className}`}>{children}</h3>
)

const CardContent = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
  <div className={`px-6 py-4 ${className}`}>{children}</div>
)

const Badge = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
    {children}
  </span>
)

interface DashboardProps {
  systemStatus: SystemStatus | null
}

export default function Dashboard({ systemStatus }: DashboardProps) {
  const [recentEvents, setRecentEvents] = useState<ClusterEvent[]>([])
  const [recentActions, setRecentActions] = useState<HealingAction[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [eventsRes, actionsRes] = await Promise.all([
          fetch('/api/events?hours=24'),
          fetch('/api/healing-actions?hours=24')
        ])
        
        if (eventsRes.ok) {
          const events = await eventsRes.json()
          setRecentEvents(events.slice(0, 10))
        }
        
        if (actionsRes.ok) {
          const actions = await actionsRes.json()
          setRecentActions(actions.slice(0, 10))
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'error': return 'bg-red-100 text-red-800'
      case 'warning': return 'bg-yellow-100 text-yellow-800'
      case 'info': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'success': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (!systemStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Activity className="mx-auto h-12 w-12 text-gray-400 animate-spin" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Loading system status...</h3>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Nodes</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStatus.nodes.ready}/{systemStatus.nodes.total}</div>
            <p className="text-xs text-muted-foreground">Ready nodes</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pods</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStatus.pods.running}/{systemStatus.pods.total}</div>
            <p className="text-xs text-muted-foreground">Running pods</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Events (24h)</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStatus.events.last_24h}</div>
            <p className="text-xs text-muted-foreground">Cluster events</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Healing Actions</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStatus.healing_actions.successful}/{systemStatus.healing_actions.last_24h}</div>
            <p className="text-xs text-muted-foreground">Successful actions</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentEvents.length === 0 ? (
                <p className="text-sm text-gray-500">No recent events</p>
              ) : (
                recentEvents.map((event) => (
                  <div key={event.id} className="flex items-start space-x-3">
                    <Badge className={getSeverityColor(event.severity)}>
                      {event.severity}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        {event.resource_name}
                        {event.namespace && (
                          <span className="text-gray-500"> ({event.namespace})</span>
                        )}
                      </p>
                      <p className="text-sm text-gray-500">{event.message}</p>
                      <p className="text-xs text-gray-400">
                        {new Date(event.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Healing Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentActions.length === 0 ? (
                <p className="text-sm text-gray-500">No recent healing actions</p>
              ) : (
                recentActions.map((action) => (
                  <div key={action.id} className="flex items-start space-x-3">
                    <Badge className={getStatusColor(action.status)}>
                      {action.status}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        {action.action_type}: {action.resource_name}
                        {action.namespace && (
                          <span className="text-gray-500"> ({action.namespace})</span>
                        )}
                      </p>
                      <p className="text-sm text-gray-500">{action.reason}</p>
                      <p className="text-xs text-gray-400">
                        {new Date(action.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Node Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(systemStatus.nodes.details).map(([nodeName, nodeData]) => (
              <div key={nodeName} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{nodeName}</h4>
                  <Badge className={nodeData.status === 'Ready' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                    {nodeData.status}
                  </Badge>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Last updated: {new Date(nodeData.timestamp).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
