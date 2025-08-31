import React, { useEffect, useState } from 'react'

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

interface Configuration {
  kubernetes: {
    in_cluster: boolean
    namespace: string
  }
  monitoring: {
    interval: number
    metrics: string[]
  }
  healing: {
    enabled: boolean
    actions: {
      restart_failed_pods: boolean
      reschedule_pending_pods: boolean
      scale_deployments: boolean
    }
    thresholds: {
      pod_restart_threshold: number
      pending_pod_timeout: number
      cpu_threshold: number
      memory_threshold: number
    }
  }
  alerts: {
    enabled: boolean
    channels: Array<{
      type: string
      enabled?: boolean
    }>
  }
  dashboard: {
    host: string
    port: number
    auth_enabled: boolean
  }
}

export default function Settings() {
  const [config, setConfig] = useState<Configuration | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('/api/config')
        if (response.ok) {
          const data = await response.json()
          setConfig(data)
        }
      } catch (error) {
        console.error('Error fetching configuration:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchConfig()
  }, [])

  if (loading) {
    return <div className="text-center py-8">Loading configuration...</div>
  }

  if (!config) {
    return <div className="text-center py-8">Failed to load configuration</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600">System configuration and settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Kubernetes Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium">In-cluster mode:</span>
                <Badge className={config.kubernetes.in_cluster ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                  {config.kubernetes.in_cluster ? 'Yes' : 'No'}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Namespace:</span>
                <span className="text-sm text-gray-600">
                  {config.kubernetes.namespace || 'All namespaces'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monitoring Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Interval:</span>
                <span className="text-sm text-gray-600">{config.monitoring.interval}s</span>
              </div>
              <div>
                <span className="text-sm font-medium">Metrics:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {config.monitoring.metrics.map((metric) => (
                    <Badge key={metric} className="bg-blue-100 text-blue-800">
                      {metric.replace('_', ' ')}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Self-Healing Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Enabled:</span>
                <Badge className={config.healing.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                  {config.healing.enabled ? 'Yes' : 'No'}
                </Badge>
              </div>
              
              <div>
                <span className="text-sm font-medium">Actions:</span>
                <div className="mt-1 space-y-1">
                  {Object.entries(config.healing.actions).map(([action, enabled]) => (
                    <div key={action} className="flex justify-between">
                      <span className="text-xs text-gray-600">{action.replace('_', ' ')}:</span>
                      <Badge className={enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {enabled ? 'On' : 'Off'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <span className="text-sm font-medium">Thresholds:</span>
                <div className="mt-1 space-y-1">
                  <div className="flex justify-between text-xs">
                    <span>Pod restart threshold:</span>
                    <span>{config.healing.thresholds.pod_restart_threshold}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span>Pending timeout:</span>
                    <span>{config.healing.thresholds.pending_pod_timeout}s</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span>CPU threshold:</span>
                    <span>{config.healing.thresholds.cpu_threshold}%</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span>Memory threshold:</span>
                    <span>{config.healing.thresholds.memory_threshold}%</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alert Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Enabled:</span>
                <Badge className={config.alerts.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                  {config.alerts.enabled ? 'Yes' : 'No'}
                </Badge>
              </div>
              
              <div>
                <span className="text-sm font-medium">Channels:</span>
                <div className="mt-1 space-y-1">
                  {config.alerts.channels.map((channel, index) => (
                    <div key={index} className="flex justify-between">
                      <span className="text-xs text-gray-600">{channel.type}:</span>
                      <Badge className={channel.enabled !== false ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {channel.enabled !== false ? 'On' : 'Off'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Dashboard Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Host:</span>
                <span className="text-sm text-gray-600">{config.dashboard.host}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Port:</span>
                <span className="text-sm text-gray-600">{config.dashboard.port}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Authentication:</span>
                <Badge className={config.dashboard.auth_enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                  {config.dashboard.auth_enabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
