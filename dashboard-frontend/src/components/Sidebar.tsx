import { NavLink } from 'react-router-dom'
import { 
  Activity, 
  Server, 
  Package, 
  AlertTriangle, 
  Wrench, 
  Bell, 
  Settings 
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Activity },
  { name: 'Nodes', href: '/nodes', icon: Server },
  { name: 'Pods', href: '/pods', icon: Package },
  { name: 'Events', href: '/events', icon: AlertTriangle },
  { name: 'Healing Actions', href: '/healing', icon: Wrench },
  { name: 'Alerts', href: '/alerts', icon: Bell },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="p-6">
        <h2 className="text-xl font-bold text-gray-900">K8s Monitor</h2>
      </div>
      <nav className="mt-6">
        <div className="px-3">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `group flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 ${
                  isActive
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
