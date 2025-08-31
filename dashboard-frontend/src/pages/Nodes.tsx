import React, { useEffect, useState } from 'react'
import { NodeMetric } from '../types'

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

export default function Nodes() {
  const [nodes, setNodes] = useState<NodeMetric[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchNodes = async () => {
      try {
        const response = await fetch('/api/metrics/nodes?hours=1')
        if (response.ok) {
          const data = await response.json()
          setNodes(data)
        }
      } catch (error) {
        console.error('Error fetching nodes:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchNodes()
    const interval = setInterval(fetchNodes, 30000)
    return () => clearInterval(interval)
  }, [])

  const getLatestNodeData = () => {
    const nodeMap = new Map<string, NodeMetric>()
    
    nodes.forEach(node => {
      const existing = nodeMap.get(node.node_name)
      if (!existing || new Date(node.timestamp) > new Date(existing.timestamp)) {
        nodeMap.set(node.node_name, node)
      }
    })
    
    return Array.from(nodeMap.values())
  }

  if (loading) {
    return <div className="text-center py-8">Loading nodes...</div>
  }

  const latestNodes = getLatestNodeData()

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Nodes</h2>
        <p className="text-gray-600">Monitor the health and status of your Kubernetes nodes</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {latestNodes.map((node) => (
          <Card key={node.node_name}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{node.node_name}</CardTitle>
                <Badge className={node.status === 'Ready' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                  {node.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <h4 className="text-sm font-medium text-gray-700">Capacity</h4>
                  <div className="mt-1 space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>CPU:</span>
                      <span>{node.cpu_capacity}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Memory:</span>
                      <span>{node.memory_capacity}</span>
                    </div>
                  </div>
                </div>

                {node.conditions && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700">Conditions</h4>
                    <div className="mt-1 space-y-1">
                      {Object.entries(node.conditions).map(([condition, status]) => (
                        <div key={condition} className="flex justify-between text-sm">
                          <span>{condition}:</span>
                          <Badge className={status === 'True' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                            {status}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-2 border-t">
                  <p className="text-xs text-gray-500">
                    Last updated: {new Date(node.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {latestNodes.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-gray-500">No node data available</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
