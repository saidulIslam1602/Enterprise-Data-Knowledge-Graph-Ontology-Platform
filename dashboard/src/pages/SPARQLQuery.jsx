import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Play, Copy, Download, Clock } from 'lucide-react'
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import toast from 'react-hot-toast'
import { executeSPARQL } from '../services/api'

const EXAMPLE_QUERIES = [
  {
    name: 'Count All Triples',
    query: `SELECT (COUNT(*) AS ?count)
WHERE {
  ?s ?p ?o
}`,
  },
  {
    name: 'List All Classes',
    query: `PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?class ?label
WHERE {
  ?class a owl:Class .
  OPTIONAL { ?class rdfs:label ?label }
}
ORDER BY ?class
LIMIT 20`,
  },
  {
    name: 'Customer Status Distribution',
    query: `PREFIX cus: <http://enterprise.org/ontology/customer#>

SELECT ?status (COUNT(?customer) AS ?count)
WHERE {
  ?customer a cus:Customer ;
            cus:customerStatus ?status .
}
GROUP BY ?status
ORDER BY DESC(?count)`,
  },
  {
    name: 'High-Value Customers',
    query: `PREFIX cus: <http://enterprise.org/ontology/customer#>

SELECT ?email ?lifetimeValue
WHERE {
  ?customer a cus:Customer ;
            cus:email ?email ;
            cus:lifetimeValue ?lifetimeValue .
  FILTER(?lifetimeValue > 10000)
}
ORDER BY DESC(?lifetimeValue)
LIMIT 10`,
  },
]

export default function SPARQLQuery() {
  const [query, setQuery] = useState(EXAMPLE_QUERIES[0].query)
  const [results, setResults] = useState(null)
  const [executionTime, setExecutionTime] = useState(null)

  const mutation = useMutation({
    mutationFn: executeSPARQL,
    onSuccess: (data) => {
      setResults(data)
      toast.success('Query executed successfully')
    },
    onError: (error) => {
      toast.error(`Query failed: ${error.message}`)
    },
  })

  const handleExecute = () => {
    const startTime = performance.now()
    mutation.mutate(query, {
      onSettled: () => {
        const endTime = performance.now()
        setExecutionTime(((endTime - startTime) / 1000).toFixed(3))
      },
    })
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(query)
    toast.success('Query copied to clipboard')
  }

  const handleDownload = () => {
    if (!results) return
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `sparql-results-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Results downloaded')
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">SPARQL Query</h2>
        <p className="text-gray-600 mt-1">
          Execute SPARQL queries on the knowledge graph
        </p>
      </div>

      {/* Example Queries */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Example Queries</h3>
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_QUERIES.map((example) => (
            <button
              key={example.name}
              onClick={() => setQuery(example.query)}
              className="btn btn-secondary text-sm"
            >
              {example.name}
            </button>
          ))}
        </div>
      </div>

      {/* Query Editor */}
      <div className="card">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Query Editor</h3>
          <div className="flex space-x-2">
            <button onClick={handleCopy} className="btn btn-secondary">
              <Copy className="w-4 h-4 mr-2" />
              Copy
            </button>
            <button
              onClick={handleExecute}
              disabled={mutation.isPending}
              className="btn btn-primary"
            >
              <Play className="w-4 h-4 mr-2" />
              {mutation.isPending ? 'Executing...' : 'Execute'}
            </button>
          </div>
        </div>

        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full h-64 p-4 font-mono text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder="Enter your SPARQL query here..."
        />

        {executionTime && (
          <div className="mt-3 flex items-center text-sm text-gray-600">
            <Clock className="w-4 h-4 mr-2" />
            Execution time: {executionTime}s
          </div>
        )}
      </div>

      {/* Results */}
      {results && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Results ({results.results?.bindings?.length || 0} rows)
            </h3>
            <button onClick={handleDownload} className="btn btn-secondary">
              <Download className="w-4 h-4 mr-2" />
              Download JSON
            </button>
          </div>

          {/* Table View */}
          {results.results?.bindings && results.results.bindings.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {results.head?.vars?.map((variable) => (
                      <th
                        key={variable}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {variable}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.results.bindings.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      {results.head?.vars?.map((variable) => (
                        <td key={variable} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row[variable]?.value || '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No results found</p>
          )}

          {/* Raw JSON View */}
          <details className="mt-4">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
              View Raw JSON
            </summary>
            <div className="mt-2">
              <SyntaxHighlighter language="json" style={atomOneDark} customStyle={{ borderRadius: '0.5rem' }}>
                {JSON.stringify(results, null, 2)}
              </SyntaxHighlighter>
            </div>
          </details>
        </div>
      )}
    </div>
  )
}
