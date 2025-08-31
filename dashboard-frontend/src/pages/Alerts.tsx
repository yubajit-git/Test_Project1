import React, { useEffect, useState } from 'react'
import { Alert } from '../types'

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

const Input = ({ className = '', ...props }: React.InputHTMLAttributes<HTMLInputElement> & { className?: string }) => (
  <input className={`block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${className}`} {...props} />
)

const Select = ({ value, onValueChange, children, className = '' }: { value: string, onValueChange: (value: string) => void, children: React.ReactNode, className?: string }) => (
  <select 
    value={value} 
    onChange={(e) => onValueChange(e.target.value)}
    className={`block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${className}`}
  >
    {children}
  </select>
)

const SelectTrigger = ({ children, className = '' }: { children: React.ReactNode, className?: string }) => (
  <div className={className}>{children}</div>
)

const SelectValue = ({ placeholder }: { placeholder: string }) => <span>{placeholder}</span>

const SelectContent = ({ children }: { children: React.ReactNode }) => <>{children}</>

const SelectItem = ({ value, children }: { value: string, children: React.ReactNode }) => (
  <option value={value}>{children}</option>
)

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [severityFilter, setSeverityFilter] = useState('all')

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch('/api/alerts')
        if (response.ok) {
          const data = await response.json()
          setAlerts(data)
        }
      } catch (error) {
        console.error('Error fetching alerts:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()
    const interval = setInterval(fetchAlerts, 30000)
    return () => clearInterval(interval)
  }, [])

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.resource_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.namespace.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         alert.message.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesSeverity = severityFilter === 'all' || alert.severity.toLowerCase() === severityFilter
    
    return matchesSearch && matchesSeverity
  })

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
      case 'active': return 'bg-red-100 text-red-800'
      case 'resolved': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading alerts...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Alerts</h2>
        <p className="text-gray-600">Monitor active alerts and notifications</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <Input
          placeholder="Search alerts..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <Select value={severityFilter} onValueChange={setSeverityFilter}>
          <SelectTrigger className="max-w-xs">
            <SelectValue placeholder="Filter by severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severities</SelectItem>
            <SelectItem value="error">Error</SelectItem>
            <SelectItem value="warning">Warning</SelectItem>
            <SelectItem value="info">Info</SelectItem>
          </SelectContent>
        </Select>
        <div className="text-sm text-gray-500 flex items-center">
          {filteredAlerts.length} alerts
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredAlerts.length === 0 ? (
              <p className="text-center text-gray-500 py-8">
                {searchTerm || severityFilter !== 'all' ? 'No alerts match your filters' : 'No active alerts'}
              </p>
            ) : (
              filteredAlerts.map((alert) => (
                <div key={alert.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge className={getSeverityColor(alert.severity)}>
                          {alert.severity}
                        </Badge>
                        <Badge className={getStatusColor(alert.status)}>
                          {alert.status}
                        </Badge>
                        <span className="text-sm font-medium">{alert.alert_type}</span>
                      </div>
                      
                      <h4 className="font-medium text-gray-900">
                        {alert.resource_name}
                        {alert.namespace && (
                          <span className="text-gray-500 font-normal"> ({alert.namespace})</span>
                        )}
                      </h4>
                      
                      {alert.message && (
                        <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                      )}
                      
                      {alert.channels_sent && Object.keys(alert.channels_sent).length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500 mb-1">Sent via:</p>
                          <div className="flex flex-wrap gap-1">
                            {Object.entries(alert.channels_sent).map(([channel, status]) => (
                              <Badge key={channel} className={status === 'SUCCESS' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                                {channel}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="text-right">
                      <p className="text-xs text-gray-500">
                        {new Date(alert.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
