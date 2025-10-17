# Enterprise Data Knowledge Graph & Ontology Platform

<div align="center">

![Knowledge Graph](https://img.shields.io/badge/Knowledge%20Graph-W3C%20Compliant-blue)
![RDF](https://img.shields.io/badge/RDF-1.1-green)
![SPARQL](https://img.shields.io/badge/SPARQL-1.1-orange)
![SHACL](https://img.shields.io/badge/SHACL-Validation-red)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)

</div>

## 🎯 Overview

Enterprise-grade semantic knowledge graph platform built with **W3C standards compliance**. This platform provides comprehensive RDF data management, SPARQL querying, SHACL validation, and multi-source data harmonization capabilities.

### Key Features

✅ **W3C Standards Compliance**
- RDF 1.1 specification
- SPARQL 1.1 Query Language
- SHACL (Shapes Constraint Language)
- OWL 2 RL reasoning
- RDFS inference

✅ **Triple Store Integration**
- Apache Jena Fuseki
- Ontotext GraphDB
- High-performance semantic storage

✅ **Advanced Query Capabilities**
- Property paths for transitive queries
- Federated SPARQL queries
- Aggregation functions (COUNT, SUM, AVG, MIN, MAX)
- Full-text search
- Query result caching

✅ **Data Quality & Validation**
- SHACL-based validation
- Quality metrics and reporting
- Automated validation history
- HTML/JSON/CSV export formats

✅ **Data Harmonization**
- Schema mapping and transformation
- Entity resolution and deduplication
- Conflict detection and resolution
- Provenance tracking (W3C PROV)

✅ **Interactive Visualization**
- D3.js-based knowledge graph visualization
- Real-time graph exploration
- Entity search and filtering
- Drag-and-drop interaction

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Dashboard                        │
│              (React + D3.js + TypeScript)                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                          │
│           (W3C-Compliant Knowledge Graph Endpoints)          │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│  W3C RDF Service          │  │  Advanced SPARQL Service  │
│  - RDF 1.1                │  │  - Property paths         │
│  - OWL 2 reasoning        │  │  - Aggregations           │
│  - RDFS inference         │  │  - Federated queries      │
│  - SKOS support           │  │  - Full-text search       │
└───────────────────────────┘  └───────────────────────────┘
                │                           │
┌───────────────────────────┐  ┌───────────────────────────┐
│  SHACL Validator          │  │  Data Harmonization       │
│  - Constraint checking    │  │  - Schema mapping         │
│  - Quality metrics        │  │  - Entity resolution      │
│  - Validation reports     │  │  - Conflict resolution    │
└───────────────────────────┘  └───────────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
        ┌────────────────────────────────────────┐
        │          Triple Stores                  │
        │  ┌──────────────┐  ┌──────────────┐   │
        │  │ Jena Fuseki  │  │   GraphDB    │   │
        │  └──────────────┘  └──────────────┘   │
        └────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/saidulIslam1602/Enterprise-Data-Knowledge-Graph-Ontology-Platform.git
cd Enterprise-Data-Knowledge-Graph-Ontology-Platform
```

2. **Configure environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

3. **Start services with Docker**
```bash
docker-compose up -d
```

This will start:
- Apache Jena Fuseki (port 3030)
- Ontotext GraphDB (port 7200)
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI Backend (port 8000)
- React Dashboard (port 3000)

4. **Initialize data**
```bash
# Generate sample data
python scripts/generate_data.py

# Validate data
python scripts/debug_and_test.py
```

5. **Access the platform**
- Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Jena Fuseki: http://localhost:3030
- GraphDB: http://localhost:7200

---

## 📚 Usage Examples

### W3C-Compliant RDF Operations

```python
from src.core.w3c_rdf_service import W3CCompliantRDFService

# Initialize service
rdf_service = W3CCompliantRDFService(base_uri="https://enterprise.example.com/")

# Create ontology metadata (Dublin Core)
rdf_service.create_ontology_metadata(
    ontology_uri="https://enterprise.example.com/ontology/customer",
    title="Customer Ontology",
    description="Enterprise customer data ontology",
    version="1.0.0",
    creators=["Enterprise Team"]
)

# Define OWL class
rdf_service.define_class(
    class_uri="https://enterprise.example.com/ontology/Customer",
    label="Customer",
    comment="Represents a business customer",
    parent_class="http://xmlns.com/foaf/0.1/Agent"
)

# Define property
rdf_service.define_property(
    property_uri="https://enterprise.example.com/ontology/hasEmail",
    label="has email",
    comment="Customer's email address",
    property_type="DatatypeProperty",
    domain="https://enterprise.example.com/ontology/Customer",
    range_="http://www.w3.org/2001/XMLSchema#string"
)

# Apply RDFS reasoning
rdf_service.apply_rdfs_reasoning()

# Apply OWL 2 RL reasoning
rdf_service.apply_owl_reasoning(profile="OWL_RL")

# Validate W3C compliance
report = rdf_service.validate_w3c_compliance()
print(report)
```

### Advanced SPARQL Queries

```python
from src.core.sparql_service import AdvancedSPARQLService
from rdflib import Graph

# Initialize
graph = Graph()
graph.parse("data/samples/generated_data.ttl", format="turtle")
sparql_service = AdvancedSPARQLService(graph)

# Find paths between resources
paths = sparql_service.find_paths(
    start_uri="https://enterprise.example.com/customer/123",
    end_uri="https://enterprise.example.com/company/456",
    max_length=5
)

# Find connected resources (transitive)
connected = sparql_service.find_connected_resources(
    resource_uri="https://enterprise.example.com/customer/123",
    depth=2
)

# Aggregation query
stats = sparql_service.aggregate_statistics(
    subject_class="https://enterprise.example.com/ontology/Customer",
    property_path="https://enterprise.example.com/ontology/hasOrderValue",
    aggregation="SUM"
)

# Full-text search
results = sparql_service.search_by_text(
    search_text="john doe",
    property_paths=[
        "http://www.w3.org/2000/01/rdf-schema#label",
        "http://xmlns.com/foaf/0.1/name"
    ]
)

# Get query statistics
query_stats = sparql_service.get_query_statistics()
print(f"Average query time: {query_stats['avg_execution_time_ms']}ms")
```

### SHACL Validation

```python
from src.core.shacl_validator import SHACLValidationService
from rdflib import Graph

# Initialize
validator = SHACLValidationService()

# Load data and shapes
data_graph = Graph()
data_graph.parse("data/samples/generated_data.ttl", format="turtle")

shapes_graph = Graph()
shapes_graph.parse("validation/customer_shapes.ttl", format="turtle")

# Validate
report = validator.validate(
    data_graph=data_graph,
    shapes_graph=shapes_graph,
    inference="rdfs",
    advanced=True
)

print(f"Conforms: {report['conforms']}")
print(f"Violations: {report['violation_count']}")
print(f"Warnings: {report['warning_count']}")

# Generate quality report
quality_report = validator.create_quality_report(report)
print(f"Quality Score: {quality_report['quality_score']}/100")

# Export report
validator.export_validation_report(report, "validation_report.html", format="html")
```

### Data Harmonization

```python
from src.core.data_harmonization import DataHarmonizationService
from rdflib import Graph

# Initialize
harmonization = DataHarmonizationService("https://enterprise.example.com/harmonized/")

# Add mapping rules
harmonization.add_mapping_rule(
    source_ontology="external_system_1",
    source_class="http://external.com/Person",
    target_class="https://enterprise.example.com/ontology/Customer",
    property_mappings={
        "http://external.com/fullName": "http://xmlns.com/foaf/0.1/name",
        "http://external.com/emailAddr": "https://enterprise.example.com/ontology/hasEmail"
    }
)

# Harmonize data
source_graph = Graph()
source_graph.parse("external_data.ttl", format="turtle")

harmonized_graph = harmonization.harmonize_graph(
    source_graph=source_graph,
    source_ontology_id="external_system_1",
    provenance_info={
        "source": "External System 1",
        "import_date": "2025-10-17"
    }
)

# Detect conflicts
conflicts = harmonization.detect_conflicts()
print(f"Conflicts found: {len(conflicts)}")

# Resolve conflicts
resolved = harmonization.resolve_conflicts(strategy="most_recent")
print(f"Resolved {resolved} conflicts")

# Validate quality
quality = harmonization.validate_data_quality()
print(f"Quality score: {quality['quality_score']}")

# Export harmonized data
harmonization.export_harmonized_data("harmonized_output.ttl", format="turtle")
```

### Triple Store Operations

```python
from src.triplestore.fuseki_client import get_fuseki_client

# Get Fuseki client
client = get_fuseki_client(
    fuseki_url="http://localhost:3030",
    dataset="enterprise_kg"
)

# Create dataset
client.create_dataset()

# Upload ontology
client.upload_ontology("ontologies/customer_ontology.ttl")

# Execute SPARQL query
query = """
PREFIX ns: <https://enterprise.example.com/ontology/>
SELECT ?customer ?name WHERE {
    ?customer a ns:Customer ;
              ns:hasName ?name .
}
LIMIT 10
"""
results = client.sparql_query(query)

# Get statistics
stats = client.get_statistics()
print(f"Total triples: {stats['triple_count']}")

# Health check
is_healthy = client.health_check()
print(f"Fuseki healthy: {is_healthy}")
```

---

## 🔌 API Endpoints

### W3C RDF Service
- `GET /api/v1/kg/ontology/metadata` - Get ontology metadata
- `POST /api/v1/kg/ontology/create-class` - Create OWL class
- `POST /api/v1/kg/ontology/create-property` - Create OWL property
- `POST /api/v1/kg/ontology/reasoning/rdfs` - Apply RDFS reasoning
- `POST /api/v1/kg/ontology/reasoning/owl` - Apply OWL reasoning
- `GET /api/v1/kg/ontology/class-hierarchy` - Get class hierarchy
- `GET /api/v1/kg/ontology/validate-w3c` - Validate W3C compliance

### Advanced SPARQL
- `POST /api/v1/kg/sparql/query` - Execute SPARQL query
- `GET /api/v1/kg/sparql/find-paths` - Find paths between resources
- `GET /api/v1/kg/sparql/connected-resources` - Get connected resources
- `GET /api/v1/kg/sparql/aggregate` - Aggregation queries
- `POST /api/v1/kg/sparql/search` - Full-text search
- `GET /api/v1/kg/sparql/class-instances` - Count class instances
- `GET /api/v1/kg/sparql/property-usage` - Property usage statistics

### SHACL Validation
- `POST /api/v1/kg/validation/validate-file` - Validate RDF file
- `POST /api/v1/kg/validation/quality-report` - Generate quality report
- `GET /api/v1/kg/validation/history` - Get validation history

### Data Harmonization
- `POST /api/v1/kg/harmonization/add-mapping` - Add mapping rule
- `POST /api/v1/kg/harmonization/harmonize` - Harmonize data
- `GET /api/v1/kg/harmonization/conflicts` - Detect conflicts
- `POST /api/v1/kg/harmonization/resolve-conflicts` - Resolve conflicts
- `GET /api/v1/kg/harmonization/quality` - Validate quality
- `GET /api/v1/kg/harmonization/statistics` - Get statistics

### Triple Store
- `GET /api/v1/kg/triplestore/health` - Health check
- `GET /api/v1/kg/triplestore/statistics` - Get statistics
- `GET /api/v1/kg/triplestore/datasets` - List datasets

---

## 🛠 Technology Stack

### Backend
- **Python 3.10+** - Core language
- **FastAPI** - Web framework
- **RDFLib** - RDF manipulation
- **PySHACL** - SHACL validation
- **SPARQLWrapper** - SPARQL client
- **OWL-RL** - OWL reasoning

### Triple Stores
- **Apache Jena Fuseki** - Primary triple store
- **Ontotext GraphDB** - Alternative triple store

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **D3.js** - Graph visualization
- **Vite** - Build tool
- **TailwindCSS** - Styling

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **PostgreSQL** - Metadata storage
- **Redis** - Caching layer
- **Nginx** - Web server

---

## 📊 Standards Compliance

This platform is compliant with the following W3C standards:

- ✅ **RDF 1.1** - Resource Description Framework
- ✅ **RDFS** - RDF Schema
- ✅ **OWL 2** - Web Ontology Language
- ✅ **SPARQL 1.1** - Query Language
- ✅ **SHACL** - Shapes Constraint Language
- ✅ **SKOS** - Simple Knowledge Organization System
- ✅ **Dublin Core** - Metadata terms
- ✅ **PROV** - Provenance Ontology
- ✅ **FOAF** - Friend of a Friend

---

## 🙏 Acknowledgments

- W3C for semantic web standards
- Apache Jena community
- Ontotext for GraphDB
- RDFLib developers

---

<div align="center">
Built with ❤️ for the semantic web community
</div>
