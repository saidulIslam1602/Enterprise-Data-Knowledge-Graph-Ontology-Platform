import { useQuery } from '@tanstack/react-query'
import { CheckCircle, XCircle, AlertTriangle, Activity } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getShapeStatistics } from '../services/api'

const QUALITY_DIMENSIONS = [
  {
    name: 'Accuracy',
    description: 'Data correctly describes real-world entities',
    score: 92,
    color: 'bg-green-500',
  },
  {
    name: 'Completeness',
    description: 'All required data is present',
    score: 88,
    color: 'bg-blue-500',
  },
  {
    name: 'Consistency',
    description: 'Data is uniform across systems',
    score: 95,
    color: 'bg-purple-500',
  },
  {
    name: 'Timeliness',
    description: 'Data is up-to-date',
    score: 85,
    color: 'bg-amber-500',
  },
  {
    name: 'Validity',
    description: 'Data conforms to business rules',
    score: 90,
    color: 'bg-pink-500',
  },
  {
    name: 'Uniqueness',
    description: 'No duplicate records',
    score: 94,
    color: 'bg-indigo-500',
  },
]

export default function DataQuality() {
  const { data: shapeStats, isLoading } = useQuery({
    queryKey: ['shape-statistics'],
    queryFn: getShapeStatistics,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const overallScore = Math.round(
    QUALITY_DIMENSIONS.reduce((sum, dim) => sum + dim.score, 0) / QUALITY_DIMENSIONS.length
  )

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Data Quality</h2>
        <p className="text-gray-600 mt-1">
          Monitor data quality metrics and SHACL validation
        </p>
      </div>

      {/* Overall Score */}
      <div className="card bg-gradient-to-br from-primary-500 to-primary-700 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm opacity-90 uppercase tracking-wide">Overall Quality Score</p>
            <div className="flex items-center mt-2">
              <p className="text-5xl font-bold">{overallScore}%</p>
              {overallScore >= 90 ? (
                <CheckCircle className="w-8 h-8 ml-3" />
              ) : overallScore >= 75 ? (
                <AlertTriangle className="w-8 h-8 ml-3" />
              ) : (
                <XCircle className="w-8 h-8 ml-3" />
              )}
            </div>
            <p className="mt-2 opacity-90">
              {overallScore >= 90
                ? 'Excellent data quality'
                : overallScore >= 75
                ? 'Good data quality, some improvements needed'
                : 'Data quality needs attention'}
            </p>
          </div>
          <Activity className="w-24 h-24 opacity-20" />
        </div>
      </div>

      {/* SHACL Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Total Shapes</p>
              <p className="stat-value mt-2">{shapeStats?.total_shapes || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-500 bg-opacity-10">
              <CheckCircle className="w-6 h-6 text-blue-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Property Shapes</p>
              <p className="stat-value mt-2">{shapeStats?.property_shapes || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-500 bg-opacity-10">
              <Activity className="w-6 h-6 text-purple-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Constraints</p>
              <p className="stat-value mt-2">{shapeStats?.constraints || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-amber-500 bg-opacity-10">
              <AlertTriangle className="w-6 h-6 text-amber-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Quality Dimensions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Data Quality Dimensions
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={QUALITY_DIMENSIONS}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="score" fill="#0ea5e9" name="Quality Score (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Dimension Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {QUALITY_DIMENSIONS.map((dimension) => (
          <div key={dimension.name} className="card">
            <div className="flex items-start justify-between mb-3">
              <h4 className="font-semibold text-gray-900">{dimension.name}</h4>
              <span className={`px-2 py-1 rounded text-xs font-medium text-white ${dimension.color}`}>
                {dimension.score}%
              </span>
            </div>
            <p className="text-sm text-gray-600">{dimension.description}</p>
            <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${dimension.color}`}
                style={{ width: `${dimension.score}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* SHACL Info */}
      <div className="card bg-purple-50 border-l-4 border-purple-500">
        <div className="flex items-start">
          <CheckCircle className="w-6 h-6 text-purple-600 mt-0.5" />
          <div className="ml-3">
            <h3 className="text-lg font-semibold text-purple-900">
              SHACL Validation Framework
            </h3>
            <p className="text-purple-700 mt-1">
              Data quality is enforced using SHACL (Shapes Constraint Language). The platform validates
              customer data, compliance records, and ontology structure against defined constraints.
            </p>
            <div className="mt-3 space-y-1 text-sm">
              <p className="text-purple-700">• Property constraints (cardinality, datatype, pattern)</p>
              <p className="text-purple-700">• SPARQL-based business rules</p>
              <p className="text-purple-700">• Automated validation on data ingestion</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
