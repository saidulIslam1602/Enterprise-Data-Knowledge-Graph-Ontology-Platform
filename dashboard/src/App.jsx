import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import SPARQLQuery from './pages/SPARQLQuery'
import Compliance from './pages/Compliance'
import DataQuality from './pages/DataQuality'
import Ontologies from './pages/Ontologies'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="sparql" element={<SPARQLQuery />} />
          <Route path="compliance" element={<Compliance />} />
          <Route path="data-quality" element={<DataQuality />} />
          <Route path="ontologies" element={<Ontologies />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
