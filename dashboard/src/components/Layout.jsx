import { Outlet, NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Database, 
  Shield, 
  CheckCircle, 
  Network,
  Github
} from 'lucide-react'

export default function Layout() {
  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/sparql', icon: Database, label: 'SPARQL Query' },
    { path: '/compliance', icon: Shield, label: 'Compliance' },
    { path: '/data-quality', icon: CheckCircle, label: 'Data Quality' },
    { path: '/ontologies', icon: Network, label: 'Ontologies' },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Network className="w-8 h-8 text-primary-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Knowledge Graph Platform
                </h1>
                <p className="text-xs text-gray-500">
                  Semantic Web & Ontology Dashboard
                </p>
              </div>
            </div>
            <a
              href="https://github.com/saidulIslam1602/Enterprise-Data-Knowledge-Graph-Ontology-Platform"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <Github className="w-5 h-5" />
              <span className="hidden sm:inline text-sm">View on GitHub</span>
            </a>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navItems.map(({ path, icon: Icon, label }) => (
              <NavLink
                key={path}
                to={path}
                className={({ isActive }) =>
                  `flex items-center space-x-2 py-4 px-2 border-b-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Enterprise Knowledge Graph & Ontology Platform • Built with React, FastAPI, and RDF
          </p>
        </div>
      </footer>
    </div>
  )
}
