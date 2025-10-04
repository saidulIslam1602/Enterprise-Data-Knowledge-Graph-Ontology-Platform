import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Database, Layers, Link2, FileText, TrendingUp } from 'lucide-react'
import { getStatistics, healthCheck } from '../services/api'

const COLORS = ['#0ea5e9', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: getStatistics,
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const statCards = [
    {
      icon: Database,
      label: 'Total Triples',
      value: stats?.total_triples?.toLocaleString() || '0',
      color: 'bg-blue-500',
    },
    {
      icon: Layers,
      label: 'OWL Classes',
      value: stats?.classes || '0',
      color: 'bg-purple-500',
    },
    {
      icon: Link2,
      label: 'Object Properties',
      value: stats?.object_properties || '0',
      color: 'bg-pink-500',
    },
    {
      icon: FileText,
      label: 'Data Properties',
      value: stats?.data_properties || '0',
      color: 'bg-amber-500',
    },
    {
      icon: TrendingUp,
      label: 'Individuals',
      value: stats?.individuals || '0',
      color: 'bg-green-500',
    },
  ]

  const propertyDistribution = [
    { name: 'Object Properties', value: stats?.object_properties || 0 },
    { name: 'Data Properties', value: stats?.data_properties || 0 },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-600 mt-1">
            Overview of your Knowledge Graph Platform
          </p>
        </div>
        {health && (
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${health.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
            <span className="text-sm text-gray-600">
              {health.status === 'healthy' ? 'System Healthy' : 'System Issues'}
            </span>
          </div>
        )}
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {statCards.map((stat) => (
          <div key={stat.label} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="stat-label">{stat.label}</p>
                <p className="stat-value mt-2">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.color} bg-opacity-10`}>
                <stat.icon className={`w-6 h-6 ${stat.color.replace('bg-', 'text-')}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Property Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Property Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={propertyDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {propertyDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Component Stats */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Ontology Components
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={[
                { name: 'Classes', count: stats?.classes || 0 },
                { name: 'Object Props', count: stats?.object_properties || 0 },
                { name: 'Data Props', count: stats?.data_properties || 0 },
                { name: 'Individuals', count: stats?.individuals || 0 },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Links */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => window.location.href = '/sparql'}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
          >
            <Database className="w-8 h-8 text-primary-600 mb-2" />
            <h4 className="font-semibold text-gray-900">Run SPARQL Query</h4>
            <p className="text-sm text-gray-600 mt-1">
              Execute custom queries on the knowledge graph
            </p>
          </button>

          <button
            onClick={() => window.location.href = '/compliance'}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
          >
            <Shield className="w-8 h-8 text-primary-600 mb-2" />
            <h4 className="font-semibold text-gray-900">Check Compliance</h4>
            <p className="text-sm text-gray-600 mt-1">
              Monitor GDPR compliance and data subject rights
            </p>
          </button>

          <button
            onClick={() => window.location.href = '/ontologies'}
            className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all"
          >
            <Network className="w-8 h-8 text-primary-600 mb-2" />
            <h4 className="font-semibold text-gray-900">Explore Ontologies</h4>
            <p className="text-sm text-gray-600 mt-1">
              Browse classes and properties
            </p>
          </button>
        </div>
      </div>
    </div>
  )
}
