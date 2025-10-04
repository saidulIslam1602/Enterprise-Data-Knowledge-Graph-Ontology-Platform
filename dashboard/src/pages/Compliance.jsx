import { useQuery } from '@tanstack/react-query'
import { Shield, AlertCircle, CheckCircle, Clock, FileText } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { getComplianceReport, getOverdueDSR, getExpiringConsents } from '../services/api'

const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function Compliance() {
  const { data: report, isLoading } = useQuery({
    queryKey: ['compliance-report'],
    queryFn: getComplianceReport,
  })

  const { data: overdueDSR } = useQuery({
    queryKey: ['overdue-dsr'],
    queryFn: () => getOverdueDSR(0),
  })

  const { data: expiringConsents } = useQuery({
    queryKey: ['expiring-consents'],
    queryFn: () => getExpiringConsents(30),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const consentData = report?.consent_summary
    ? Object.entries(report.consent_summary)
        .filter(([key]) => key !== 'total')
        .map(([name, value]) => ({ name, value }))
    : []

  const dsrData = report?.dsr_summary
    ? Object.entries(report.dsr_summary)
        .filter(([key]) => key !== 'total' && key !== 'overdue')
        .map(([name, value]) => ({ name, value }))
    : []

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">GDPR Compliance</h2>
        <p className="text-gray-600 mt-1">
          Monitor compliance status and data subject rights
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Total Consents</p>
              <p className="stat-value mt-2">{report?.consent_summary?.total || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-green-500 bg-opacity-10">
              <Shield className="w-6 h-6 text-green-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Active Consents</p>
              <p className="stat-value mt-2">{report?.consent_summary?.ACTIVE || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-500 bg-opacity-10">
              <CheckCircle className="w-6 h-6 text-blue-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">DSR Requests</p>
              <p className="stat-value mt-2">{report?.dsr_summary?.total || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-500 bg-opacity-10">
              <FileText className="w-6 h-6 text-purple-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Overdue DSR</p>
              <p className="stat-value mt-2 text-red-600">
                {overdueDSR?.count || 0}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-red-500 bg-opacity-10">
              <AlertCircle className="w-6 h-6 text-red-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Consent Status Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Consent Status Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            {consentData.length > 0 ? (
              <PieChart>
                <Pie
                  data={consentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {consentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                No consent data available
              </div>
            )}
          </ResponsiveContainer>
        </div>

        {/* DSR Request Status */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            DSR Request Status
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            {dsrData.length > 0 ? (
              <BarChart data={dsrData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8b5cf6" />
              </BarChart>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                No DSR data available
              </div>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts */}
      {overdueDSR?.count > 0 && (
        <div className="card bg-red-50 border-l-4 border-red-500">
          <div className="flex items-start">
            <AlertCircle className="w-6 h-6 text-red-600 mt-0.5" />
            <div className="ml-3">
              <h3 className="text-lg font-semibold text-red-900">
                Overdue Data Subject Rights Requests
              </h3>
              <p className="text-red-700 mt-1">
                You have {overdueDSR.count} overdue DSR request{overdueDSR.count > 1 ? 's' : ''}. 
                GDPR requires responses within 30 days.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Expiring Consents */}
      {expiringConsents?.count > 0 && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Clock className="w-5 h-5 text-amber-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Consents Expiring Soon ({expiringConsents.count})
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Consent ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Purpose
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Days Until Expiry
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Expiry Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {expiringConsents.consents?.slice(0, 5).map((consent) => (
                  <tr key={consent.consent_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {consent.consent_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {consent.purpose}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          consent.days_until_expiry <= 7
                            ? 'bg-red-100 text-red-800'
                            : consent.days_until_expiry <= 14
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {consent.days_until_expiry} days
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {new Date(consent.expiry_date).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Compliance Info */}
      <div className="card bg-blue-50 border-l-4 border-blue-500">
        <div className="flex items-start">
          <Shield className="w-6 h-6 text-blue-600 mt-0.5" />
          <div className="ml-3">
            <h3 className="text-lg font-semibold text-blue-900">
              GDPR Compliance Framework
            </h3>
            <p className="text-blue-700 mt-1">
              This platform implements GDPR Articles 5, 6, 12, 15-22, and 33. Monitor consent management,
              data subject rights requests, and breach notifications.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
