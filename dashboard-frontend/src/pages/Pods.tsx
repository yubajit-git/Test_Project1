import React, { useEffect, useState } from 'react'
import { PodMetric } from '../types'

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

export default function Pods() {
  const [pods, setPods] = useState<PodMetric[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const fetchPods = async () => {
      try {
        const response = await fetch('/api/metrics/pods?hours=1')
        if (response.ok) {
          const data = await response.json()
          setPods(data)
        }
      } catch (error) {
        console.error('Error fetching pods:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPods()
    const interval = setInterval(fetchPods, 30000)
    return () => clearInterval(interval)
  }, [])

  const getLatestPodData = () => {
    const podMap = new Map<string, PodMetric>()
    
    pods.forEach(pod => {
      const key = `${pod.namespace}/${pod.pod_name}`
      const existing = podMap.get(key)
      if (!existing || new Date(pod.timestamp) > new Date(existing.timestamp)) {
        podMap.set(key, pod)
      }
    })
    
    return Array.from(podMap.values())
  }

  const filteredPods = getLatestPodData().filter(pod =>
    pod.pod_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pod.namespace.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (status: string, ready: boolean) => {
    if (status === 'Running' && ready) return 'bg-green-100 text-green-800'
    if (status === 'Failed') return 'bg-red-100 text-red-800'
    if (status === 'Pending') return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return <div className="text-center py-8">Loading pods...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Pods</h2>
        <p className="text-gray-600">Monitor the health and status of your Kubernetes pods</p>
      </div>

      <div className="flex justify-between items-center">
        <Input
          placeholder="Search pods..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <div className="text-sm text-gray-500">
          {filteredPods.length} pods
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredPods.map((pod) => (
          <Card key={`${pod.namespace}/${pod.pod_name}`}>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-base">{pod.pod_name}</CardTitle>
                  <p className="text-sm text-gray-500">{pod.namespace}</p>
                </div>
                <Badge className={getStatusColor(pod.status, pod.ready)}>
                  {pod.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Ready:</span>
                  <Badge className={pod.ready ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                    {pod.ready ? 'Yes' : 'No'}
                  </Badge>
                </div>
                
                <div className="flex justify-between text-sm">
                  <span>Restarts:</span>
                  <span className={pod.restart_count > 5 ? 'text-red-600 font-medium' : ''}>
                    {pod.restart_count}
                  </span>
                </div>
                
                {pod.node_name && (
                  <div className="flex justify-between text-sm">
                    <span>Node:</span>
                    <span className="text-gray-600">{pod.node_name}</span>
                  </div>
                )}

                <div className="pt-2 border-t">
                  <p className="text-xs text-gray-500">
                    Last updated: {new Date(pod.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredPods.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-gray-500">
              {searchTerm ? 'No pods match your search' : 'No pod data available'}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
