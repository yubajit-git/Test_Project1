import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Nodes from './pages/Nodes'
import Pods from './pages/Pods'
import Events from './pages/Events'
import HealingActions from './pages/HealingActions'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'
import { SystemStatus } from './types'

function App() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.host}/api/ws`)
    
    ws.onopen = () => {
      setIsConnected(true)
      ws.send('status_request')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'status_update') {
        setSystemStatus(data.data)
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
    }
    
    ws.onerror = () => {
      setIsConnected(false)
    }

    const interval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('status_request')
      }
    }, 30000)

    return () => {
      clearInterval(interval)
      ws.close()
    }
  }, [])

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">
                  Kubernetes Health Monitor
                </h1>
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-sm text-gray-600">
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>
            
            <Routes>
              <Route path="/" element={<Dashboard systemStatus={systemStatus} />} />
              <Route path="/nodes" element={<Nodes />} />
              <Route path="/pods" element={<Pods />} />
              <Route path="/events" element={<Events />} />
              <Route path="/healing" element={<HealingActions />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

export default App
