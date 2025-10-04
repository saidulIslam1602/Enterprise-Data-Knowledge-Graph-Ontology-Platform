import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Statistics
export const getStatistics = async () => {
  const { data } = await api.get('/statistics')
  return data
}

// SPARQL Queries
export const executeSPARQL = async (query, format = 'json') => {
  const { data } = await api.post('/sparql/query', { query, format })
  return data
}

// Ontologies
export const getOntologyClasses = async () => {
  const { data } = await api.get('/ontology/classes')
  return data
}

export const getOntologyProperties = async () => {
  const { data } = await api.get('/ontology/properties')
  return data
}

// Compliance
export const getComplianceReport = async () => {
  const { data } = await api.get('/compliance/report')
  return data
}

export const checkGDPRCompliance = async (dataSubjectId) => {
  const { data } = await api.get(`/compliance/gdpr/${dataSubjectId}`)
  return data
}

export const getOverdueDSR = async (daysOverdue = 0) => {
  const { data } = await api.get('/compliance/dsr/overdue', {
    params: { days_overdue: daysOverdue }
  })
  return data
}

export const getExpiringConsents = async (daysAhead = 30) => {
  const { data } = await api.get('/compliance/consents/expiring', {
    params: { days_ahead: daysAhead }
  })
  return data
}

// Validation
export const validateData = async (dataContent, format = 'turtle') => {
  const { data } = await api.post('/validate', { data: dataContent, format })
  return data
}

export const getShapeStatistics = async () => {
  const { data } = await api.get('/validation/shapes/statistics')
  return data
}

// Health check
export const healthCheck = async () => {
  const { data } = await api.get('/health')
  return data
}

export default api
