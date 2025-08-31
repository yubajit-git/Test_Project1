import React, { useEffect, useState } from 'react'
import { HealingAction } from '../types'

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

export default function HealingActions() {
  const [actions, setActions] = useState<HealingAction[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    const fetchActions = async () => {
      try {
        const response = await fetch('/api/healing-actions?hours=24')
        if (response.ok) {
          const data = await response.json()
          setActions(data)
        }
      } catch (error) {
        console.error('Error fetching healing actions:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchActions()
    const interval = setInterval(fetchActions, 30000)
    return () => clearInterval(interval)
  }, [])

  const filteredActions = actions.filter(action => {
    const matchesSearch = action.resource_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         action.namespace.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         action.action_type.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || action.status.toLowerCase() === statusFilter
    
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'success': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getActionTypeColor = (actionType: string) => {
    switch (actionType.toLowerCase()) {
      case 'restart_pod': return 'bg-blue-100 text-blue-800'
      case 'reschedule_pod': return 'bg-purple-100 text-purple-800'
      case 'scale_deployment': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading healing actions...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Healing Actions</h2>
        <p className="text-gray-600">Monitor automated self-healing actions performed by the system</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <Input
          placeholder="Search actions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="max-w-xs">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="success">Success</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
          </SelectContent>
        </Select>
        <div className="text-sm text-gray-500 flex items-center">
          {filteredActions.length} actions
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Healing Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredActions.length === 0 ? (
              <p className="text-center text-gray-500 py-8">
                {searchTerm || statusFilter !== 'all' ? 'No actions match your filters' : 'No healing actions available'}
              </p>
            ) : (
              filteredActions.map((action) => (
                <div key={action.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge className={getActionTypeColor(action.action_type)}>
                          {action.action_type.replace('_', ' ')}
                        </Badge>
                        <Badge className={getStatusColor(action.status)}>
                          {action.status}
                        </Badge>
                      </div>
                      
                      <h4 className="font-medium text-gray-900">
                        {action.resource_name}
                        {action.namespace && (
                          <span className="text-gray-500 font-normal"> ({action.namespace})</span>
                        )}
                      </h4>
                      
                      {action.reason && (
                        <p className="text-sm text-gray-600 mt-1">
                          <span className="font-medium">Reason:</span> {action.reason}
                        </p>
                      )}
                      
                      {action.result && (
                        <p className="text-sm text-gray-600 mt-1">
                          <span className="font-medium">Result:</span> {action.result}
                        </p>
                      )}
                    </div>
                    
                    <div className="text-right">
                      <p className="text-xs text-gray-500">
                        {new Date(action.timestamp).toLocaleString()}
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
