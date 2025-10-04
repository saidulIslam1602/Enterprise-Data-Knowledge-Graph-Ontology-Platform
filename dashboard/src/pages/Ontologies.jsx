import { useQuery } from '@tanstack/react-query'
import { Network, Box, Link2, FileText, Search } from 'lucide-react'
import { useState } from 'react'
import { getOntologyClasses, getOntologyProperties } from '../services/api'

export default function Ontologies() {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('classes') // 'classes' or 'properties'

  const { data: classes, isLoading: classesLoading } = useQuery({
    queryKey: ['ontology-classes'],
    queryFn: getOntologyClasses,
  })

  const { data: properties, isLoading: propertiesLoading } = useQuery({
    queryKey: ['ontology-properties'],
    queryFn: getOntologyProperties,
  })

  const isLoading = classesLoading || propertiesLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const filteredClasses = classes?.classes?.filter((cls) =>
    cls.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const filteredObjectProps = properties?.object_properties?.filter((prop) =>
    prop.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const filteredDataProps = properties?.data_properties?.filter((prop) =>
    prop.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const extractLabel = (uri) => {
    const parts = uri.split(/[#/]/)
    return parts[parts.length - 1] || uri
  }

  const extractNamespace = (uri) => {
    const match = uri.match(/^(.*[#/])[^#/]+$/)
    return match ? match[1] : uri
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Ontologies</h2>
        <p className="text-gray-600 mt-1">
          Explore OWL classes and properties
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Classes</p>
              <p className="stat-value mt-2">{classes?.count || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-500 bg-opacity-10">
              <Box className="w-6 h-6 text-blue-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Object Properties</p>
              <p className="stat-value mt-2">{properties?.object_properties?.length || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-500 bg-opacity-10">
              <Link2 className="w-6 h-6 text-purple-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Data Properties</p>
              <p className="stat-value mt-2">{properties?.data_properties?.length || 0}</p>
            </div>
            <div className="p-3 rounded-lg bg-green-500 bg-opacity-10">
              <FileText className="w-6 h-6 text-green-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search classes and properties..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('classes')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'classes'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Box className="w-4 h-4" />
                <span>Classes ({filteredClasses.length})</span>
              </div>
            </button>
            <button
              onClick={() => setActiveTab('properties')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'properties'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Network className="w-4 h-4" />
                <span>Properties ({filteredObjectProps.length + filteredDataProps.length})</span>
              </div>
            </button>
          </nav>
        </div>

        <div className="mt-6">
          {activeTab === 'classes' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredClasses.length > 0 ? (
                filteredClasses.map((cls) => (
                  <div
                    key={cls}
                    className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all cursor-pointer"
                  >
                    <div className="flex items-start space-x-3">
                      <Box className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-gray-900 truncate">
                          {extractLabel(cls)}
                        </h4>
                        <p className="text-xs text-gray-500 mt-1 truncate">
                          {extractNamespace(cls)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-2 text-center py-12 text-gray-500">
                  No classes found
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Object Properties */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Link2 className="w-5 h-5 mr-2 text-purple-600" />
                  Object Properties ({filteredObjectProps.length})
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredObjectProps.length > 0 ? (
                    filteredObjectProps.map((prop) => (
                      <div
                        key={prop}
                        className="p-4 border border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all cursor-pointer"
                      >
                        <div className="flex items-start space-x-3">
                          <Link2 className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-gray-900 truncate">
                              {extractLabel(prop)}
                            </h4>
                            <p className="text-xs text-gray-500 mt-1 truncate">
                              {extractNamespace(prop)}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 text-center py-8 text-gray-500">
                      No object properties found
                    </div>
                  )}
                </div>
              </div>

              {/* Data Properties */}
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-green-600" />
                  Data Properties ({filteredDataProps.length})
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredDataProps.length > 0 ? (
                    filteredDataProps.map((prop) => (
                      <div
                        key={prop}
                        className="p-4 border border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all cursor-pointer"
                      >
                        <div className="flex items-start space-x-3">
                          <FileText className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-gray-900 truncate">
                              {extractLabel(prop)}
                            </h4>
                            <p className="text-xs text-gray-500 mt-1 truncate">
                              {extractNamespace(prop)}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 text-center py-8 text-gray-500">
                      No data properties found
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Info Card */}
      <div className="card bg-blue-50 border-l-4 border-blue-500">
        <div className="flex items-start">
          <Network className="w-6 h-6 text-blue-600 mt-0.5" />
          <div className="ml-3">
            <h3 className="text-lg font-semibold text-blue-900">
              Ontology Structure
            </h3>
            <p className="text-blue-700 mt-1">
              The platform includes 5 comprehensive ontologies: Customer, Company, Compliance, Data Lineage, 
              and Business Glossary. These ontologies are built using OWL 2, follow W3C standards, and 
              support multi-language labels (English/Norwegian).
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
